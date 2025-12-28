# Task 3: Categorization & Trend Analysis - Summary

## 🔄 What's Running

The categorization script is currently processing all 1,004 articles to:
1. Classify articles by Civil Engineering areas
2. Classify articles by AI technologies
3. Create co-occurrence matrix
4. Generate heatmap visualization

## 📊 Classification Categories

### Civil Engineering Areas:
1. **Structural** - Analysis, design, health monitoring, materials
2. **Geotechnical** - Soil, foundations, tunnels, excavation
3. **Transportation** - Traffic, roads, autonomous vehicles, logistics
4. **Construction Management** - Scheduling, safety, cost estimation, site monitoring
5. **Environmental Engineering** - Sustainability, waste management, green building

### AI Technologies:
1. **Computer Vision** - Image recognition, drone inspection, safety monitoring
2. **Predictive Analytics** - Risk assessment, maintenance prediction
3. **Generative Design** - Optimization, parametric modeling
4. **Robotics/Automation** - Robots, autonomous machinery
5. **Machine Learning** - Neural networks, deep learning, algorithms
6. **Artificial Intelligence** - General AI applications

## 🎯 Expected Outputs

### Files Created:
- `articles_classified_*.csv` - Articles with classification tags
- `cooccurrence_matrix_*.csv` - Matrix of CE Areas × AI Technologies
- `cooccurrence_heatmap.png` - Visual heatmap
- `categorization_report_*.txt` - Analysis report

### Key Results:
- Count of articles per CE area
- Count of articles per AI technology
- Co-occurrence frequencies
- **Answer to main question:** Which CE area uses AI most?

## 📈 Analysis Features

### Classification Method:
- Keyword-based matching (dictionary approach)
- Case-insensitive matching
- Multiple tags allowed per article
- Uses title, content, and processed text

### Co-occurrence Matrix:
- Rows: Civil Engineering Areas (5)
- Columns: AI Technologies (6)
- Values: Number of articles with both tags
- Visualized as heatmap

## ⏱️ Processing Time

- **Estimated:** 1-2 minutes for 1,004 articles
- Includes classification, matrix calculation, and visualization

## ✅ Deliverables Status

- [x] Classification script created
- [ ] Processing in progress...
- [ ] Classified articles CSV (will be saved)
- [ ] Co-occurrence matrix (will be saved)
- [ ] Heatmap visualization (will be generated)
- [ ] Analysis report (will be created)

## 🎯 Main Question

**"Which Civil Engineering area is using AI the most?"**

The script will rank all CE areas by their AI usage and provide the answer!

---

**Status:** Processing articles... Check back in a minute!


