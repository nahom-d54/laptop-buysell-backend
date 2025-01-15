from django.core.management.base import BaseCommand
from laptops.models import LaptopPost, SimilarityScore
from Levenshtein import ratio
from concurrent.futures import ThreadPoolExecutor


class Command(BaseCommand):
    help = "Precompute similarity scores for all items based on multiple attributes"

    def handle(self, *args, **kwargs):
        items = LaptopPost.objects.all()

        # Generate batches for efficiency
        batch_size = 100
        batches = self.generate_batches(items, batch_size)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for batch in batches:
                futures.append(
                    executor.submit(self.compute_similarities_for_batch, batch)
                )

            # Wait for all the futures to complete
            for future in futures:
                future.result()

        self.stdout.write(
            self.style.SUCCESS("Successfully precomputed similarity scores.")
        )

    def generate_batches(self, items, batch_size):
        """
        Generates batches of LaptopPost items for efficient processing.
        """
        for i in range(0, len(items), batch_size):
            yield items[i : i + batch_size]

    def compute_similarities_for_batch(self, batch):
        """
        Computes the similarity scores for a batch of LaptopPost items.
        """
        similarity_scores = []
        for item_a in batch:
            for item_b in batch:
                if item_a != item_b:
                    similarity_score = self.compute_similarity(item_a, item_b)
                    if (
                        similarity_score is not None
                    ):  # Only add valid SimilarityScore objects
                        similarity_scores.append(similarity_score)

        # Use bulk_create to insert the batch into the database at once
        if similarity_scores:
            SimilarityScore.objects.bulk_create(similarity_scores)

    def compute_similarity(self, item_a, item_b):
        """
        Computes the similarity score between two LaptopPost items.
        """
        # Check if similarity score already exists
        if SimilarityScore.objects.filter(item_a=item_a, item_b=item_b).exists():
            return None  # Skip if already computed

        # 1. Name similarity using Levenshtein ratio
        name_a = item_a.title.lower() if item_a.title else ""
        name_b = item_b.title.lower() if item_b.title else ""

        storage_a = item_a.storage.lower() if item_a.storage else ""
        storage_b = item_b.storage.lower() if item_b.storage else ""

        processor_a = item_a.processor.lower() if item_a.processor else ""
        processor_b = item_b.processor.lower() if item_b.processor else ""

        ram_a = item_a.ram.lower() if item_a.ram else ""
        ram_b = item_b.ram.lower() if item_b.ram else ""

        name_similarity = ratio(name_a, name_b)
        storage_similarity = ratio(storage_a, storage_b)
        processor_similarity = ratio(processor_a, processor_b)
        ram_similarity = ratio(ram_a, ram_b)

        # 4. Weighted combined similarity
        total_similarity = (
            0.2 * name_similarity
            + 0.3 * storage_similarity
            + 0.3 * processor_similarity
            + 0.2 * ram_similarity
        )

        # Create the SimilarityScore object
        return SimilarityScore(
            item_a=item_a,
            item_b=item_b,
            score=total_similarity,
        )
