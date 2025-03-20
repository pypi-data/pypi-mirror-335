import os
import pandas as pd
from rich.console import Console
from rich.table import Table
import re
import nltk
from nltk.tokenize import word_tokenize
from importlib import resources  # Menggunakan importlib.resources untuk akses sumber daya

class AsroNLP:
    def __init__(self):
        with resources.path('asro_nlp.data', 'stopwords.txt') as p:
            self.stopwords_path = str(p)
        self.initialize_paths()
        self.load_resources()

    def initialize_paths(self):
        base_dir = os.path.dirname(self.stopwords_path)
        self.normalization_path = os.path.join(base_dir, "kamuskatabaku.xlsx")
        self.news_dictionary_path = os.path.join(base_dir, "news_dictionary.txt")
        self.root_words_path = os.path.join(base_dir, "kata-dasar.txt")
        self.lexicon_positive_path = os.path.join(base_dir, "kamus_positive.xlsx")
        self.lexicon_negative_path = os.path.join(base_dir, "kamus_negative.xlsx")

    def load_resources(self):
        self.ensure_files_exist([
            self.stopwords_path,
            self.normalization_path,
            self.news_dictionary_path,
            self.root_words_path,
            self.lexicon_positive_path,
            self.lexicon_negative_path
        ])
        nltk.download('punkt', quiet=True)
        self.stopwords = self.load_stopwords()
        self.normalization_dict = self.load_excel_dict(self.normalization_path)
        self.lexicon_positive_dict = self.load_excel_dict(self.lexicon_positive_path)
        self.lexicon_negative_dict = self.load_excel_dict(self.lexicon_negative_path)
        self.news_media = self.load_news_media()

    def ensure_files_exist(self, files):
        missing_files = [file for file in files if not os.path.exists(file)]
        if missing_files:
            raise FileNotFoundError(f"Required file(s) not found: {', '.join(missing_files)}")

    def load_stopwords(self):
        with open(self.stopwords_path, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())

    def load_excel_dict(self, path):
        df = pd.read_excel(path, header=None, engine='openpyxl')
        return dict(zip(df[0].str.lower(), df[1]))

    def load_news_media(self):
        with open(self.news_dictionary_path, "r", encoding="utf-8") as f:
            return set(self.normalize_media_name(line.strip()) for line in f.readlines())

    @staticmethod
    def normalize_media_name(name):
        name = re.sub(r"[^\w\d\s.]", '', name)
        name = re.sub(r"\s+", ' ', name)
        return name.lower()

    @staticmethod
    def case_folding(text):
        return text.lower()

    @staticmethod
    def clean_text(text):
        text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
        text = re.sub(r"\@\w+|\#", "", text)
        text = re.sub(r"\d+", "", text)
        text = re.sub(r"[^\w\s]", "", text)
        return text.strip()

    @staticmethod
    def tokenize_text(text):
        return word_tokenize(text)

    def remove_stopwords(self, tokens):
        return [token for token in tokens if token not in self.stopwords and token.isalpha()]

    def normalize_text(self, tokens):
        return [self.normalization_dict.get(token, token) for token in tokens]

    def custom_stemmer(self, token):
        if isinstance(token, str):
            return token[:-1] if token.endswith('ing') else token
        else:
            raise ValueError("Stemmer function expected a string, got a list instead")

    def sentiment_analysis(self, tokens):
        score = 0
        positive_words = []
        negative_words = []
        for word in tokens:
            word = word.lower()
            if word in self.lexicon_positive_dict:
                score += self.lexicon_positive_dict[word]
                positive_words.append(word)
            if word in self.lexicon_negative_dict:
                score += self.lexicon_negative_dict[word]  # Adjust scoring for negatives
                negative_words.append(word)

        # Debug output to trace the computation
        print(f"Tokens: {tokens}")
        print(f"Score: {score}, Positive words: {positive_words}, Negative words: {negative_words}")

        # Determine sentiment based on adjusted scoring
        if score > 0:
            sentiment = 'Positive'
        elif score < 0:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'

        return {
            'Sentiment': sentiment,
            'Positive_Words': ', '.join(positive_words),
            'Negative_Words': ', '.join(negative_words)
        }

    def preprocess_and_analyze(self, input_path, output_path="output.xlsx"):
        console = Console()
        try:
            df = pd.read_excel(input_path, engine='openpyxl')
            df = self.process_dataframe(df)
            sentiment_counts = df['Sentiment'].value_counts()
            source_type_counts = df['Source_Type'].value_counts()

            # Tabel untuk sentiment counts
            sentiment_table = Table(title="Sentiment Counts", title_style="bold magenta")
            sentiment_table.add_column("Sentiment", style="dim", justify="right")
            sentiment_table.add_column("Count", justify="right")
            for sentiment, count in sentiment_counts.items():
                sentiment_table.add_row(sentiment, str(count))
            console.print(sentiment_table)

            # Tabel untuk source type counts
            source_type_table = Table(title="Source Type Counts", title_style="bold magenta")
            source_type_table.add_column("Source Type", style="dim", justify="right")
            source_type_table.add_column("Count", justify="right")
            for source_type, count in source_type_counts.items():
                source_type_table.add_row(source_type, str(count))
            console.print(source_type_table)

            df.to_excel(output_path, index=False, engine='openpyxl')
            console.print(f"[bold green]Processed data saved to {output_path}[/bold green]")

            # ASCII art logo
            logo = r"""
            ___   _____ _________________   _________    __  ________  ___
            / _ | / __/ // /  _/_  __/ __/  / __/ _ \ \  / / / /_  __/ / _ \\
            / __ |_\ \/ _  // /  / / / _/   / _// , _/ | |/ / /__ / /  / , _/
            /_/ |_/___/_//_/___/ /_/ /___/  /___/_/|_| |___/____/ /_/ /_/|_|
            """
            console.print("[bold blue]" + logo + "[/bold blue]")

            console.print("[bold yellow]Terima kasih telah menggunakan library AsroNLP, yang dikembangkan oleh Asro untuk keperluan edukasi dan pengembangan analisis sentimen.[/bold yellow]")
        except Exception as e:
            console.print(f"[bold red]Error processing data: {e}[/bold red]")


    def process_dataframe(self, df):
        text_column = 'full_text' if 'full_text' in df.columns else 'comment'
        df['Case_Folded_Text'] = df[text_column].apply(self.case_folding)
        df['Cleaned_Text'] = df['Case_Folded_Text'].apply(self.clean_text)

        # Hapus baris jika 'Cleaned_Text' kosong atau hanya berisi spasi
        df = df[df['Cleaned_Text'].str.strip().ne('')].copy()

        df['Tokens'] = df['Cleaned_Text'].apply(self.tokenize_text)
        df['Filtered_Tokens'] = df['Tokens'].apply(self.remove_stopwords)
        df['Normalized_Text'] = df['Filtered_Tokens'].apply(self.normalize_text)
        
        df['Stemmed_Text'] = df['Normalized_Text'].apply(lambda tokens: [self.custom_stemmer(token) for token in tokens if isinstance(token, str)])
        df['Sentiment_Results'] = df['Stemmed_Text'].apply(self.sentiment_analysis)
        
        # Update DataFrame using .loc to set values correctly
        df.loc[:, 'Sentiment'] = df['Sentiment_Results'].apply(lambda x: x['Sentiment'])
        df.loc[:, 'Positive_Words'] = df['Sentiment_Results'].apply(lambda x: x['Positive_Words'])
        df.loc[:, 'Negative_Words'] = df['Sentiment_Results'].apply(lambda x: x['Negative_Words'])

        channel_title_column = 'channel_title' if 'channel_title' in df.columns else 'username' if 'username' in df.columns else None
        if channel_title_column is None:
            raise ValueError("DataFrame does not contain a recognized channel title column ('channel_title' or 'username').")
        
        df.loc[:, 'Source_Type'] = df.apply(lambda x: self.detect_source_type(x[channel_title_column]), axis=1)

        # Hapus kolom sementara
        df.drop(['Sentiment_Results', 'Case_Folded_Text', 'Stemmed_Text'], axis=1, inplace=True)
        return df




    def detect_source_type(self, source_identifier):
        if not isinstance(source_identifier, str):
            return 'Individual'
        normalized_identifier = self.normalize_media_name(source_identifier)
        return 'Media' if any(media_name in normalized_identifier for media_name in self.news_media) else 'Individual'
