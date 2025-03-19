from typing import Dict, Any, List
from kirara_ai.plugin_manager.plugin import Plugin
from kirara_ai.logger import get_logger
from dataclasses import dataclass
from kirara_ai.workflow.core.block import BlockRegistry
from kirara_ai.ioc.inject import Inject
from kirara_ai.ioc.container import DependencyContainer
from kirara_ai.workflow.core.workflow.builder import WorkflowBuilder
from kirara_ai.workflow.core.workflow.registry import WorkflowRegistry
from .blocks import WeatherSearchBlock,RandomGirlVideoBlock,RandomCosplayBlock,RandomEmojiBlock,SougouImageSearchBlock,CutOffPrefix,BilibiliRexBlock,BilibiliSearchBlock
logger = get_logger("ApiCollection")
import importlib.resources
import os
from pathlib import Path

class ApiCollectionPlugin(Plugin):
    def __init__(self, block_registry: BlockRegistry, container: DependencyContainer):
        super().__init__()
        self.block_registry = block_registry
        self.workflow_registry = container.resolve(WorkflowRegistry)
        self.container = container

    def on_load(self):
        logger.info("ApiCollectionPlugin loading")

        # 注册Block
        try:
            self.block_registry.register("weather_search", "search", WeatherSearchBlock)
            self.block_registry.register("random_girl_video", "video", RandomGirlVideoBlock)
            self.block_registry.register("random_cosplay", "image", RandomCosplayBlock)
            self.block_registry.register("random_emoji", "image", RandomEmojiBlock)
            self.block_registry.register("sougou_image_search", "image", SougouImageSearchBlock)
            self.block_registry.register("cut_off_prefix", "internal", CutOffPrefix,"文本: 截断前置文本")
            self.block_registry.register("bilibili_rex", "video", BilibiliRexBlock)
            self.block_registry.register("bilibili_search", "video", BilibiliSearchBlock)
        except Exception as e:
            logger.warning(f"ApiCollectionPlugin failed: {e}")




    def on_start(self):
        try:
            # Get current file's absolute path
            with importlib.resources.path('api_collection', '__init__.py') as p:
                package_path = p.parent
                example_dir = package_path / 'example'

                if not example_dir.exists():
                    raise FileNotFoundError(f"Example directory not found at {example_dir}")

                yaml_files = list(example_dir.glob('*.yaml')) + list(example_dir.glob('*.yml'))

                for yaml in yaml_files:
                    logger.info(yaml)
                    self.workflow_registry.register_preset_workflow("api", yaml.stem, WorkflowBuilder.load_from_yaml(os.path.join(example_dir, yaml), self.container))
        except Exception as e:
            logger.warning(f"workflow_registry failed: {e}")
            try:
                current_file = os.path.abspath(__file__)
                parent_dir = os.path.dirname(current_file)
                example_dir = os.path.join(parent_dir, 'example')
                yaml_files = [f for f in os.listdir(example_dir) if f.endswith('.yaml') or f.endswith('.yml')]

                for yaml in yaml_files:
                    logger.info(os.path.join(example_dir, yaml))
                    self.workflow_registry.register_preset_workflow("api", yaml.stem, WorkflowBuilder.load_from_yaml(os.path.join(example_dir, yaml), self.container))
            except Exception as e:
                logger.warning(f"workflow_registry failed: {e}")
        logger.info("ApiCollectionPlugin started")

    def on_stop(self):
        logger.info("ApiCollectionPlugin stopped")

