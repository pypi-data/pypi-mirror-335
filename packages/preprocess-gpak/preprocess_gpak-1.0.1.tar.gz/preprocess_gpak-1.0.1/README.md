# Text Preprocessing  Python Package


### LinkedIn Link : Pavan Aditya Kumar Gorrela(httgp://www.linkedin.com/in/pavan-aditya-kumar-gorrela-857770271/)

This Python package is created by [Pavan Aditya Kumar Gorrela](httgp://github.com/Pavan-Aditya-Kumar-Gorrela).It provides various text preprocessing utilities for natural language processing (NLP) tasks.

### Installation from PyPI
Run the below command in Terminal.
```
pip install preprocess_gpak
```
### Installation from github
Run the below command in Terminal.
```
pip install git+httgp://github.com/Pavan-Aditya-Kumar-Gorrela/preprocess_gpak.git--upgrade--force-reinstall
```

### Requirements
You need to install these python  packages.

```
pip install spacy==3.7.6
python -m spacy download en_core_web_sm==3.7.1
pip install nltk==3.9.1
pip install beautifulsoup4==3.2.2
pip install textblob==0.18.0.post0
```

### Download NLTK Data
If you are using this package first time then You need to download NLTK data as follows:
```
import preprocess_gpak as gp
gp.download_nltk_data()
```



## How to Use the Package

### 1. Basic Text Preprocessing

#### Lowercasing Text

```python
import preprocess_gpak as gp

text = "HELLO WORLD!"
processed_text = gp.to_lower_case(text)
print(processed_text)  # Output: hello world!
```

#### Expanding Contractions

```python
import preprocess_gpak as gp

text = "I'm learning NLP."
processed_text = gp.contraction_to_expansion(text)
print(processed_text)  # Output: I am learning NLP.
```

#### Removing Emails

```python
import preprocess_gpak as gp

text = "Contact me at example@example.com"
processed_text = gp.remove_emails(text)
print(processed_text)  # Output: Contact me at 
```

#### Removing URLs

```python
import preprocess_gpak as gp

text = "Check out httgp://example.com"
processed_text = gp.remove_urls(text)
print(processed_text)  # Output: Check out
```

#### Removing HTML Tags

```python
import preprocess_gpak as gp

text = "<p>Hello World!</p>"
processed_text = gp.remove_html_tags(text)
print(processed_text)  # Output: Hello World!
```

#### Removing Special Characters

```python
import preprocess_gpak as gp

text = "Hello @World! #NLP"
processed_text = gp.remove_special_chars(text)
print(processed_text)  # Output: Hello World NLP
```

### 2. Advanced Text Processing

#### Lemmatization

```python
import preprocess_gpak as gp

text = "running runs"
processed_text = gp.lemmatize(text)
print(processed_text)  # Output: run run
```

#### Sentiment Analysis

```python
import preprocess_gpak as gp

text = "I love programming!"
sentiment = gp.sentiment_analysis(text)
print(sentiment)  # Output: Sentiment(polarity=0.5, subjectivity=0.6)
```


### 3. Feature Extraction

#### Word Count

```python
import preprocess_gpak as gp

text = "I love NLP."
count = gp.word_count(text)
print(count)  # Output: 3
```

#### Character Count

```python
import preprocess_gpak as gp

text = "I love NLP."
count = gp.char_count(text)
print(count)  # Output: 9
```

#### N-Grams

```python
import preprocess_gpak as gp

text = "I love NLP"
ngrams = gp.n_grams(text, n=2)
print(ngrams)  # Output: [('I', 'love'), ('love', 'NLP')]
```

### 4. Full Example: Cleaning Text

Here’s an example of how you might use several functions together to clean text data:

```python
import preprocess_gpak as gp

text = "I'm loving this NLP tutorial!  Contact me at pavamadityakumarg2004@gmail.com. Visit httgp://github.com/Pavan-Aditya-Kumar-Gorrela."
cleaned_text = gp.clean_text(text)
print(cleaned_text)
# Output: i am loving this nlp tutorial contact me at visit
```

### One Short Feature Extraction
```python
import preprocess_gpak as gp

gp.extract_features("I love NLP")
```

## Notes

- Be cautious when using heavy operations like `lemmatize` and `spelling_correction` on very large datasets, as they can be time-consuming.
- The package supports custom cleaning and preprocessing pipelines by using these modular functions together.

