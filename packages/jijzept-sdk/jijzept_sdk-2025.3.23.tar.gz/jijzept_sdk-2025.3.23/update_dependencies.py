"""
注意事項: このスクリプトを実行するには`httpx`をpip installしておく必要があります。
"""

import asyncio
import re

import httpx


async def get_latest_versions(package_names: set[str]) -> dict[str, str]:
    """
    パッケージ名の集合を受け取り、各パッケージの最新バージョンを取得する関数
    戻り値は {パッケージ名: 最新バージョン} の辞書の形です
    この関数はPyPI JSON APIを利用して最新バージョンを取得しています
    """
    async with httpx.AsyncClient() as client:
        tasks = [
            client.get(f"https://pypi.org/pypi/{package_name}/json")
            for package_name in package_names
        ]
        results = await asyncio.gather(*tasks)
        results_json = [result.json() for result in results]
    return {
        result_json["info"]["name"] : result_json["info"]["version"]
        for result_json in results_json
    }


async def update_dependencies():
    with open("pyproject.toml", "r") as f:
        pyproject_toml = f.read()

    # "[パッケージ名] == [バージョン]" の形の文字列を抽出
    pattern = r'"((.+) == .+)"'
    matches = re.findall(pattern, pyproject_toml)
    # {'jijmodeling == 1.10.0': 'jijmodeling'} のような形式の辞書を作成
    # この辞書のキーが元の依存関係を定義する文字列である
    old_dependency_to_package_name = {
        old_dependency: package_name for old_dependency, package_name in matches
    }
    # パッケージ名の集合を作成し、重複を除去してから、各パッケージ毎に最新バージョンを取得
    package_names = set(old_dependency_to_package_name.values())
    latest_versions = await get_latest_versions(package_names)
    # {'jijmodeling': 'jijmodeling == 1.11.0'} のような形式の辞書を作成
    # この辞書の値が最新のバージョンを依存関係として定義する文字列である
    package_name_to_new_dependency = {
        package_name: f'{package_name} == {latest_versions[package_name]}'
        for package_name in latest_versions.keys()
    }
    # 元の依存関係を定義する文字列を、最新のバージョンを依存関係として定義する文字列に置換
    new_pyproject_toml = pyproject_toml
    for old_dependency, package_name in old_dependency_to_package_name.items():
        new_dependency = package_name_to_new_dependency[package_name]
        new_pyproject_toml = new_pyproject_toml.replace(old_dependency, new_dependency)

    with open("pyproject.toml", "w") as f:
        f.write(new_pyproject_toml)


if __name__ == "__main__":
    asyncio.run(update_dependencies())
