# Preprocessing Quick Reference

## 🔄 Complete Pipeline Flow

```
Raw Text
    ↓
[Normalization]
    ├─ Lowercasing
    ├─ Remove punctuation
    └─ Remove numbers/special chars
    ↓
[Tokenization]
    └─ Split into words
    ↓
[Stopword Removal]
    └─ Remove common words
    ↓
[Lemmatization]
    └─ Convert to root form
    ↓
Clean Text (Ready for Analysis)
```

---

## 📝 Terminology

### NLTK (Natural Language Toolkit)
- **Python library** for NLP
- Provides tools for text processing
- Industry standard

### Tokenization
- **Splitting text into words**
- Example: "AI in construction" → ["AI", "in", "construction"]

### Normalization
- **Standardizing text format**
- Lowercasing, removing special chars
- Makes text uniform

### Stopwords
- **Common words** with little meaning
- Examples: "the", "a", "is", "in"
- Usually removed

### Lemmatization
- **Converting words to root form**
- Example: "machines" → "machine"
- More accurate than stemming

### N-grams
- **Sequences of N words**
- Unigrams (1), Bigrams (2), Trigrams (3)
- Capture context/phrases

### TF-IDF
- **Term Frequency-Inverse Document Frequency**
- Measures word importance
- High score = important word

---

## ⚡ Quick Examples

### Before Preprocessing:
```
"AI (2025) is transforming the construction industry!"
```

### After Preprocessing:
```
"artificial intelligence transforming construction industry"
```

### Changes:
- ✅ Lowercased
- ✅ Removed "(2025)" and "!"
- ✅ Removed stopwords: "is", "the"
- ✅ Lemmatized: "transforming" → "transform" (simplified)

---

## 🎯 Key Benefits

1. **Consistency:** Same words treated as same
2. **Noise Reduction:** Removes irrelevant info
3. **Better Analysis:** More accurate results
4. **Efficiency:** Smaller, cleaner datasets

---

## 📊 Our Results

- **473 articles** preprocessed
- **14.3 tokens** per article (average)
- **2,856 unique tokens**
- **Top word:** "construction" (161 times)
- **Top bigram:** "artificial intelligence" (105 times)


