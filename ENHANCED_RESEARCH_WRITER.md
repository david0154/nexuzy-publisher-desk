# Enhanced Research Writer Documentation

## Overview

The Enhanced Research Writer is an advanced AI-powered research module for Nexuzy Publisher Desk that provides comprehensive topic research, multi-source data collection, and hallucination protection.

## 🎯 Key Features

### 1. **Topic Expansion & Deep Explanation**
- Automatically expands topics with context and related concepts
- Extracts keywords and generates subtopics
- Provides comprehensive topic explanations
- Creates optimized search queries

### 2. **Multi-Source Research Integration**

The system researches from multiple authoritative sources:

#### **GitHub Repository Search**
- Searches for relevant open-source projects
- Collects repository information (stars, description, language)
- Provides direct links to repositories
- Credibility score: 0.85

#### **Wikipedia Integration**
- Fetches comprehensive Wikipedia articles
- Extracts images from Wikipedia pages
- Provides structured content with sections
- Credibility score: 0.9

#### **DuckDuckGo Search**
- Uses DuckDuckGo Instant Answer API
- Collects abstracts and related topics
- Gathers relevant images
- Credibility score: 0.8

#### **Web Search (Fallback)**
- General web search for additional sources
- Credibility score: 0.75

### 3. **Topic Link Options**

Provides direct access links to:
- GitHub repositories with topic relevance
- Wikipedia articles
- DuckDuckGo search results
- Web sources with credibility scoring

Each link includes:
- URL
- Title
- Source type
- Credibility score

### 4. **Image Collection**

Automatically collects and filters images:
- Wikipedia article images
- DuckDuckGo image results
- Web source images
- Filters out logos and icons
- Relevance scoring for each image
- Up to 10 relevant images per article

### 5. **Hallucination Protection & Fact Verification**

#### **Multi-Source Fact Verification**
- Verifies facts against multiple sources
- Requires minimum 2 sources for verification
- Confidence threshold: 0.7 (70%)
- Cross-references claims across sources

#### **Source Credibility Scoring**
```python
Credibility Weights:
- Academic: 1.0
- Government: 0.95
- Established Media: 0.85
- Wikipedia: 0.8
- GitHub: 0.75
- General: 0.6
```

#### **Verification Process**
1. Extract factual statements from content
2. Check each fact against all collected sources
3. Calculate confidence score based on supporting sources
4. Assign credibility score based on source quality
5. Only include facts meeting verification threshold
6. Track verification rate in article metadata

### 6. **Protected Report Generation**

Generated reports include:
- Verified facts with confidence scores
- Source attribution for each claim
- Credibility scores for sources
- Verification statistics
- Quality score (1-10 scale)

## 📊 Quality Metrics

Each article includes comprehensive quality metrics:

- **Word Count**: Actual words generated
- **Quality Score**: 1-10 based on:
  - Word count target achievement
  - Source diversity (more sources = higher score)
  - Fact verification rate
  - Content structure

- **Sources Used**: Total number of sources consulted
- **Verified Facts**: Number of facts passing verification
- **Verification Rate**: Percentage of facts verified
- **Images Collected**: Number of relevant images found
- **Generation Time**: Time taken to complete research

## 🚀 Usage

### Basic Usage

```python
from core.research_writer_enhanced import EnhancedResearchWriter

# Initialize
writer = EnhancedResearchWriter(
    db_path='nexuzy.db',
    model_path='models/mistral-7b-instruct.gguf'  # Optional
)

# Write article
result = writer.write_research_article(
    topic="Artificial Intelligence in Healthcare",
    length="Long (2000-3000 words)",
    style="Investigative",
    workspace_id=1
)

# Access results
print(f"Article: {result['article']}")
print(f"Quality Score: {result['quality_score']}/10")
print(f"Sources: {result['sources_used']}")
print(f"Verified Facts: {result['verified_facts_count']}")
print(f"Images: {result['images_collected']}")
```

### With Progress Tracking

```python
def progress_callback(progress, status):
    print(f"[{progress}%] {status}")

writer.set_progress_callback(progress_callback)
result = writer.write_research_article(topic="Climate Change Solutions")
```

## 🔧 Configuration

### Source Configuration

```python
writer.sources_config = {
    'github': {'enabled': True, 'weight': 0.9},
    'wikipedia': {'enabled': True, 'weight': 0.95},
    'duckduckgo': {'enabled': True, 'weight': 0.8},
    'web_search': {'enabled': True, 'weight': 0.75}
}
```

### Verification Settings

```python
writer.verification_threshold = 0.7  # Minimum confidence (0-1)
writer.min_sources = 2  # Minimum sources to verify a fact
```

## 📦 Required Dependencies

```bash
pip install requests beautifulsoup4 llama-cpp-python
```

## 🎨 Article Styles

- **Investigative**: Deep dive, research-focused
- **Academic**: Formal, scholarly tone
- **News Report**: Current events, factual
- **Feature Story**: Narrative, engaging
- **Opinion Piece**: Analysis with perspective

## 📏 Article Lengths

- **Short**: 500-800 words
- **Medium**: 1000-1500 words
- **Long**: 2000-3000 words
- **Deep Dive**: 3000+ words

## 🛡️ Hallucination Protection Details

### How It Works

1. **Fact Extraction**: Identifies factual statements in source material
2. **Cross-Verification**: Checks each fact against multiple sources
3. **Confidence Scoring**: Calculates confidence based on source agreement
4. **Credibility Weighting**: Applies source quality weights
5. **Threshold Filtering**: Only includes high-confidence facts
6. **Transparency**: Reports verification stats in metadata

### Example Verification Result

```json
{
  "fact": "AI systems can diagnose diseases with 95% accuracy",
  "verified": true,
  "confidence": 0.85,
  "supporting_sources": [
    "Wikipedia: Artificial Intelligence in Healthcare",
    "DuckDuckGo: Medical AI Research",
    "GitHub: medical-ai-diagnostics"
  ],
  "credibility_score": 0.82
}
```

## 🔍 Research Workflow

```
1. Topic Input
   ↓
2. Topic Expansion (keywords, subtopics, queries)
   ↓
3. Multi-Source Research
   ├── GitHub (repos, code examples)
   ├── Wikipedia (articles, images)
   ├── DuckDuckGo (search results, instant answers)
   └── Web Search (additional sources)
   ↓
4. Data Collection
   ├── Links (with credibility scores)
   ├── Images (filtered and relevant)
   └── Facts (extracted from sources)
   ↓
5. Fact Verification (Hallucination Protection)
   ├── Cross-reference facts
   ├── Calculate confidence
   └── Filter by threshold
   ↓
6. Article Generation
   ├── Use AI model (if available)
   └── Template-based generation (fallback)
   ↓
7. Quality Scoring
   ↓
8. Final Article with Metadata
```

## 📈 Performance Metrics

- **Research Time**: 10-30 seconds depending on sources
- **Article Generation**: 5-15 seconds with AI model
- **Total Time**: ~20-45 seconds for complete article
- **Source Diversity**: 5-15 sources per article
- **Fact Verification Rate**: Typically 70-85%

## 🔄 Integration with Nexuzy Publisher Desk

The enhanced research writer integrates seamlessly with the existing application:

1. **Main Application**: Uses `EnhancedResearchWriter` class
2. **Progress Updates**: Real-time UI progress updates
3. **Result Display**: Shows article with all metadata
4. **Draft Saving**: Can save researched articles as drafts
5. **Export Options**: Copy, save to file, or publish

## 🐛 Error Handling

The system includes comprehensive error handling:

- Network failures (timeouts, connection errors)
- API rate limiting
- Missing data graceful degradation
- Model loading failures (falls back to templates)
- Invalid topics or queries

## 🔮 Future Enhancements

- [ ] Academic paper database integration (arXiv, PubMed)
- [ ] Real-time news API integration
- [ ] Video content research and embedding
- [ ] Citation format generation (APA, MLA, Chicago)
- [ ] Multi-language research support
- [ ] Advanced plagiarism detection
- [ ] Sentiment analysis of sources
- [ ] Automated figure/chart generation

## 📝 Example Output Structure

```json
{
  "success": true,
  "article": "# Topic\n\nArticle content...",
  "topic": "Artificial Intelligence",
  "word_count": 2450,
  "quality_score": 8.5,
  "sources_used": 12,
  "verified_facts_count": 18,
  "images_collected": 7,
  "generation_time": "23.4s",
  "sources": [
    {
      "url": "https://en.wikipedia.org/wiki/AI",
      "title": "Wikipedia: Artificial Intelligence",
      "type": "wikipedia",
      "credibility": 0.9
    }
  ],
  "images": [
    {
      "url": "https://example.com/image.jpg",
      "source": "wikipedia",
      "description": "AI neural network",
      "relevance_score": 0.8
    }
  ],
  "hallucination_protection": {
    "total_facts_checked": 25,
    "verified_facts": 18,
    "verification_rate": 0.72
  }
}
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional source integrations
- Enhanced verification algorithms
- Better image filtering
- Improved article generation templates
- Performance optimizations

## 📄 License

Same as Nexuzy Publisher Desk main project (MIT License)

## 👥 Support

For issues or questions:
- Open a GitHub issue
- Check existing documentation
- Review example code

---

**Enhanced Research Writer** - Bringing reliable, multi-source research to AI-powered content creation.
