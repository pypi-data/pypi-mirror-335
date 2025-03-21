from pathlib import Path
from datetime import datetime
import hashlib
import httpx
import yaml
import json

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy

from ..utils.log import logger


async def download_docs(
    root_url: str,
    output_dir: str,
    max_depth: int = 1,
    include_external: bool = False,
):
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=max_depth,
            include_external=include_external,
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True,
    )
    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun(root_url, config=config)

        logger.info(f"Crawled {len(results)} pages in total")

        logger.info("Saving results to files...")
        for result in results:
            logger.info(f"URL: {result.url}")
            logger.info(f"Depth: {result.metadata.get('depth', 0)}")
            file_name = result.url.split("/")[-1].split("#")[0] + ".md"
            file_path = output_dir / file_name
            logger.info(f"Saving to {file_path}")
            with open(file_path, "w", encoding="utf-8") as f:
                try:
                    f.write(result.markdown.raw_markdown)
                except Exception as e:
                    logger.error(e)


async def download_single_file(url: str, output_path: str):
    try:  
        async with httpx.AsyncClient() as client:  
            async with client.stream("GET", url) as response:  
                response.raise_for_status()  
                with open(output_path, "wb") as file:  
                    async for chunk in response.aiter_bytes():  
                        file.write(chunk)  
        logger.info(f"File downloaded to {output_path}")  
    except Exception as e:  
        logger.error(f"Failed to download file: {e}")  


def remove_duplicates(input_dir: str):
    # remove duplicates by text hash
    hashes = set()
    for file in Path(input_dir).glob("*.md"):
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
            hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if hash in hashes:
                file.unlink()
            else:
                hashes.add(hash)


def remove_prefix(text: str, spliter="#"):
    prefix = text.split(spliter)[0]
    return text.replace(prefix, "")


def remove_prefix_from_files(dir: str, spliter="# "):
    for file in Path(dir).glob("*.md"):
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
            text = remove_prefix(text, spliter)
            with open(file, "w", encoding="utf-8") as f:
                f.write(text)


async def download_item(item: dict, output_dir: str | Path):
    dir = output_dir
    if item["type"] == "package documentation":
        await download_docs(item["url"], dir)
        remove_duplicates(dir)
        remove_prefix_from_files(dir)
    elif item["type"] == "github readme":
        dir = Path(dir)
        dir.mkdir(parents=True, exist_ok=True)
        await download_single_file(item["url"], dir / "README.md")
    else:
        logger.error(f"Unknown item type: {item['type']}")


async def build_vector_db(name: str, db_item: dict, output_dir: str):
    from .vectordb import VectorDB
    root_dir = Path(output_dir) / name
    root_dir.mkdir(parents=True, exist_ok=True)
    with open(root_dir / "metadata.yaml", "w", encoding="utf-8") as f:
        yaml.dump(db_item, f)
    db = VectorDB(root_dir)
    item_infos_path = root_dir / "items_info.json"
    if item_infos_path.exists():
        with open(item_infos_path, "r", encoding="utf-8") as f:
            item_infos = json.load(f)
    else:
        item_infos = {}

    for name, item in db_item["items"].items():
        if name in item_infos:
            item_info = item_infos[name]
        else:
            item_info = {"name": name, "type": item["type"], "url": item["url"]}
        if item_info.get("status") == "success":
            logger.info(f"Item {name} already exists, skipping")
            continue
        try:
            docs_dir = root_dir / "raw" / name
            logger.info(f"Downloading item {name}")
            if not item_info.get("download_complete"):
                await download_item(item, docs_dir)
                item_info["download_complete"] = True
            else:
                logger.info(f"Item {name} already downloaded, skipping")
            # insert into database
            for file in docs_dir.glob("*.md"):
                logger.info(f"Inserting {file} from {name} into database")
                try:
                    await db.insert_from_file(file, {"source": name, "url": item["url"]})
                except Exception as e:
                    logger.error(f"Failed to insert file {file} from {name}: {e}")
                    continue
            item_info["status"] = "success"
            item_info["created_at"] = datetime.now().isoformat()
        except Exception as e:
            logger.error(f"Failed to process item {name}: {e}")
            item_info["status"] = "failed"
            item_info["error"] = str(e)
        item_infos[name] = item_info
    with open(item_infos_path, "w", encoding="utf-8") as f:
        json.dump(item_infos, f, indent=4)


async def build_all(yaml_path: str, output_dir: str):
    with open(yaml_path, "r", encoding="utf-8") as f:
        yaml_data = yaml.safe_load(f)

        for db_name in yaml_data:
            type_ = yaml_data[db_name]["type"]
            logger.info(f"Building {db_name} database")
            if type_ == "vector_db":
                await build_vector_db(db_name, yaml_data[db_name], output_dir)
            else:
                logger.error(f"Unsupported database type: {type_}")

    logger.info("Done")
