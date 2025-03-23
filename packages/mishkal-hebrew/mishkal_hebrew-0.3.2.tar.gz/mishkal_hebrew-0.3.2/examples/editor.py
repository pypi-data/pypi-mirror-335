"""
uv sync
uv pip install "gradio>=5.15.0"
uv run gradio examples/editor.py
"""

from mishkal import phonemize, normalize
import gradio as gr

default_text = """
כָּל עֶרֶב יָאִיר (הַשֵּׁם הַמָּלֵא וּמְקוֹם הָעֲבוֹדָה שֶׁלּוֹ שְׁמוּרִים בַּמַּעֲרֶכֶת) רָץ 20 קִילוֹמֶטֶר. הוּא מְסַפֵּר לִי שֶׁזֶּה מְנַקֶּה לוֹ אֶת הָרֹאשׁ אַחֲרֵי הָעֲבוֹדָה, "שָׁעָה וָחֵצִי בְּלִי עֲבוֹדָה, אִשָּׁה וִילָדִים" כְּמוֹ שֶׁהוּא מַגְדִּיר זֹאת. אֲבָל אַחֲרֵי הַמִּקְלַחַת הוּא מַתְחִיל בְּמָה שֶׁנִּתָּן לְכַנּוֹת הָעֲבוֹדָה הַשְּׁנִיָּה שֶׁלּוֹ: לִמְצֹא לוֹ קוֹלֵגוֹת חֲדָשׁוֹת לָעֲבוֹדָה, כִּי יָאִיר הוּא כַּנִּרְאֶה הַמֶּלֶךְ שֶׁל "חָבֵר מֵבִיא חָבֵר" בְּיִשְׂרָאֵל.
"""

theme = gr.themes.Soft(font=[gr.themes.GoogleFont("Roboto")])


def on_submit_debug(text: str) -> str:
    phonemes = phonemize(text, preserve_punctuation=True)
    normalized_text = normalize(text)
    return phonemes + "\n\nNormalized:\n" + normalized_text


def on_submit(text: str) -> str:
    return phonemize(text, preserve_punctuation=False)


with gr.Blocks(theme=theme) as demo:
    text_input = gr.Textbox(
        value=default_text, label="Text", rtl=True, elem_classes=["input"]
    )
    checkbox = gr.Checkbox(value=False, label="Enable Debug Mode")
    phonemes_output = gr.Textbox(label="Phonemes")
    submit_button = gr.Button("Create")

    submit_button.click(
        fn=lambda text, debug: on_submit_debug(text) if debug else on_submit(text),
        inputs=[text_input, checkbox],
        outputs=[phonemes_output],
    )


if __name__ == "__main__":
    demo.launch()
