"""
将工作区根目录的 Locke_dataset 导入数据库。

用法：
    python manage.py import_dataset
    python manage.py import_dataset --dataset "D:/path/to/Locke_dataset"

命令会：
  1. 读取 France_Pages.csv（列：image_Path, image_name, text）；
  2. 把对应 PNG 复制到 MEDIA_ROOT/manuscripts/ 下；
  3. 创建 / 更新 Collection 与 ManuscriptPage 记录（官方转写作为 ground truth）。
"""
import csv
import re
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from manuscripts.models import Collection, ManuscriptPage

CSV_MAX_FIELD = 10_000_000


class Command(BaseCommand):
    help = "导入 Locke_dataset 手稿数据集到数据库"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dataset",
            default=str(settings.BASE_DIR.parent / "Locke_dataset"),
            help="Locke_dataset 目录路径（默认在项目根目录）",
        )

    def handle(self, *args, **options):
        csv.field_size_limit(CSV_MAX_FIELD)
        dataset_dir = Path(options["dataset"]).resolve()
        csv_path = dataset_dir / "France_Pages.csv"

        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f"未找到 CSV：{csv_path}"))
            return

        collection, _ = Collection.objects.update_or_create(
            slug="france-pages",
            defaults={
                "title": "法国旅行日记",
                "subtitle": "Locke's French Journals, 1675–1679",
                "description": (
                    "约翰·洛克于 1675 至 1679 年旅居法国期间所写的旅行日记与观察笔记，"
                    "内容涵盖旅途见闻、城市风物、宗教与学术机构的考察，是研究洛克早期"
                    "思想与近代欧洲社会的珍贵一手材料。"
                ),
                "period": "1675–1679",
                "language": "英语（含少量拉丁语、法语）",
            },
        )

        media_dir = Path(settings.MEDIA_ROOT) / "manuscripts"
        media_dir.mkdir(parents=True, exist_ok=True)

        created, updated, skipped = 0, 0, 0
        with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                image_name = (row.get("image_name") or "").strip()
                text = (row.get("text") or "").strip()
                if not image_name:
                    continue

                # 定位源图片：优先 CSV 中的相对路径，其次在数据集内查找。
                rel_path = (row.get("image_Path") or "").strip().replace("\\", "/")
                candidates = [
                    dataset_dir / rel_path,
                    dataset_dir / "France_Pages" / image_name,
                    dataset_dir / image_name,
                ]
                src = next((c for c in candidates if c.exists()), None)
                if src is None:
                    self.stderr.write(
                        self.style.WARNING(f"跳过（找不到图片）：{image_name}")
                    )
                    skipped += 1
                    continue

                dest = media_dir / image_name
                if not dest.exists():
                    shutil.copy2(src, dest)

                page_number = self._extract_page_number(image_name)
                obj, is_created = ManuscriptPage.objects.update_or_create(
                    collection=collection,
                    image_name=image_name,
                    defaults={
                        "page_number": page_number,
                        "image": f"manuscripts/{image_name}",
                        "transcription": text,
                    },
                )
                if is_created:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"导入完成：新增 {created}，更新 {updated}，跳过 {skipped}。"
                f" 集合「{collection.title}」共 {collection.page_count} 页。"
            )
        )

    @staticmethod
    def _extract_page_number(image_name: str) -> int:
        match = re.search(r"(\d+)", image_name)
        return int(match.group(1)) if match else 0
