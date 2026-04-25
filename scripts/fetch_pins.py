"""
fetch_pins.py
-------------
Fetches zbaezbae's pinned GitHub repositories via the GraphQL API
and writes the result to data/pins.json.

Required secret: GH_TOKEN (classic or fine-grained, read:user scope)
"""

import os
import json
import requests
from pathlib import Path

GITHUB_USERNAME = "zbaezbae"
GH_TOKEN = os.environ["GH_TOKEN"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    pinnedItems(first: 6, types: REPOSITORY) {
      nodes {
        ... on Repository {
          name
          description
          url
          stargazerCount
          forkCount
          primaryLanguage {
            name
            color
          }
          repositoryTopics(first: 6) {
            nodes {
              topic {
                name
              }
            }
          }
          updatedAt
          isPrivate
          homepageUrl
        }
      }
    }
  }
}
"""

def fetch_pinned_repos():
    headers = {
        "Authorization": f"bearer {GH_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"query": QUERY, "variables": {"login": GITHUB_USERNAME}}
    response = requests.post(
        "https://api.github.com/graphql",
        headers=headers,
        json=payload,
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise ValueError(f"GraphQL errors: {data['errors']}")

    nodes = data["data"]["user"]["pinnedItems"]["nodes"]

    repos = []
    for node in nodes:
        topics = [t["topic"]["name"] for t in node["repositoryTopics"]["nodes"]]
        repos.append({
            "name": node["name"],
            "description": node["description"] or "",
            "url": node["url"],
            "stars": node["stargazerCount"],
            "forks": node["forkCount"],
            "language": node["primaryLanguage"]["name"] if node["primaryLanguage"] else None,
            "languageColor": node["primaryLanguage"]["color"] if node["primaryLanguage"] else "#767777",
            "topics": topics,
            "updatedAt": node["updatedAt"],
            "homepageUrl": node["homepageUrl"] or "",
        })

    return repos


def main():
    print(f"Fetching pinned repos for @{GITHUB_USERNAME}...")
    repos = fetch_pinned_repos()
    print(f"Found {len(repos)} pinned repo(s).")

    out_path = Path(__file__).parent.parent / "data" / "pins.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(repos, indent=2, ensure_ascii=False))
    print(f"Written to {out_path}")


if __name__ == "__main__":
    main()
