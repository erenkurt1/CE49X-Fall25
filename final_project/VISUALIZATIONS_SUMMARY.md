# N-grams Visualizations - Summary

## ✅ Visualizations Created

All visualizations have been generated and saved to `visualizations/` directory.

### 1. **Top Bigrams Bar Chart** (`top_bigrams.png`)
- Horizontal bar chart showing top 20 bigrams
- Color-coded with frequency values
- Shows phrases like "artificial intelligence", "machine learning", etc.

### 2. **Top Trigrams Bar Chart** (`top_trigrams.png`)
- Horizontal bar chart showing top 20 trigrams
- Color-coded with frequency values
- Shows 3-word phrases like "artificial intelligence machine", etc.

### 3. **Combined N-grams** (`ngrams_combined.png`)
- Side-by-side comparison of top 15 bigrams and trigrams
- Easy comparison view

### 4. **Bigrams Word Cloud** (`bigrams_wordcloud.png`)
- Visual word cloud representation
- Size indicates frequency
- Colorful and visually appealing

## 📊 Key Findings from Visualizations

### Top Bigrams:
1. **artificial intelligence** (105 occurrences) - Most common phrase
2. **machine learning** (46 occurrences)
3. **neural network** (30 occurrences)
4. **computer vision** (14 occurrences)
5. **construction industry** (16 occurrences)
6. **civil engineering** (15 occurrences)

### Top Trigrams:
1. **artificial intelligence machine** (12 occurrences)
2. **using artificial intelligence** (12 occurrences)
3. **ready mix concrete** (12 occurrences)
4. **structural health monitoring** (10 occurrences)

## 📁 File Locations

All visualizations are in:
```
final_project/visualizations/
├── top_bigrams.png
├── top_trigrams.png
├── ngrams_combined.png
└── bigrams_wordcloud.png
```

## 🎨 Visualization Features

- **High resolution:** 300 DPI (suitable for reports)
- **Professional styling:** Clean, modern design
- **Color-coded:** Different color schemes for different n-gram types
- **Frequency labels:** Values shown on bars
- **Ready for reports:** Can be included in final report

## 🔄 Regenerate Visualizations

To regenerate visualizations with different settings:

```bash
python scripts/visualize_ngrams.py
```

The script automatically finds the latest n-grams data file and generates all visualizations.

## 📝 Usage in Report

These visualizations can be directly included in your final report:
- Use `top_bigrams.png` and `top_trigrams.png` for the deliverables
- Use `ngrams_combined.png` for a compact view
- Use `bigrams_wordcloud.png` for visual appeal

---

**All visualizations are ready for Task 2 deliverables!**


