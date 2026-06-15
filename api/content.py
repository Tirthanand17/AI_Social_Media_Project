from nlp.caption_generator import generate_caption, generate_multiple_captions
from nlp.hashtag_generator import hashtag_strategy
from nlp.content_moderator import moderate_text
from nlp.plagiarism_checker import check_plagiarism
from nlp.image_generator import generate_prompt_package


def build_content_package(topic, platform="Instagram", tone="engaging"):
    caption = generate_caption(topic, platform, tone)
    return {
        "caption": caption,
        "hashtags": hashtag_strategy(caption, platform),
        "moderation": moderate_text(caption),
        "plagiarism": check_plagiarism(caption),
        "image_prompt": generate_prompt_package(topic, platform),
    }


def build_caption_options(topic, platform="Instagram", count=3):
    return generate_multiple_captions(topic, count, platform)
