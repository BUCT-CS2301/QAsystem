<template>
  <div class="home-container">
    <header class="header">
      <div class="logo">
        <span class="logo-icon">🏺</span>
        <span class="logo-text">文物知识问答系统</span>
      </div>
      <nav class="nav">
        <router-link to="/" class="nav-link active">首页</router-link>
        <router-link to="/qa" class="nav-link">知识问答</router-link>
        <router-link to="/about" class="nav-link">关于系统</router-link>
      </nav>
    </header>

    <main class="main-content">
      <section class="hero">
        <h1 class="hero-title">探索文物的奥秘</h1>
        <p class="hero-subtitle">基于知识图谱与大语言模型的智能问答系统</p>
        <div class="hero-actions">
          <router-link to="/qa" class="btn-primary">开始问答</router-link>
        </div>
      </section>

      <section class="features">
        <h2 class="section-title">系统特点</h2>
        <div class="feature-grid">
          <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>知识图谱支撑</h3>
            <p>基于知识图谱数据，确保回答的事实准确性</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3>大语言模型</h3>
            <p>结合LLM生成自然流畅的回答，避免机械感</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <h3>答案溯源</h3>
            <p>每条回答附带数据来源，增强可信度</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">💬</div>
            <h3>自然语言交互</h3>
            <p>支持从简单查询到复杂推理的多层次问答</p>
          </div>
        </div>
      </section>

      <section class="preview">
        <h2 class="section-title">问答示例</h2>
        <div class="preview-list">
          <div class="preview-item">
            <span class="preview-question">这件文物现藏于哪家博物馆？</span>
          </div>
          <div class="preview-item">
            <span class="preview-question">该文物属于哪个历史时期？</span>
          </div>
          <div class="preview-item">
            <span class="preview-question">这件书画作品的作者是谁？</span>
          </div>
          <div class="preview-item">
            <span class="preview-question">与该文物风格相似的文物有哪些？</span>
          </div>
        </div>
      </section>
    </main>

    <footer class="footer">
      <p>&copy; 2024 文物知识问答系统 - 基于知识图谱与大语言模型构建</p>
    </footer>
  </div>
</template>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 5%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.logo-icon {
  font-size: 1.5rem;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 600;
  color: white;
}

.nav {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  transition: all 0.3s ease;
}

.nav-link:hover,
.nav-link.active {
  background: rgba(255, 255, 255, 0.2);
}

.main-content {
  flex: 1;
  padding: 2rem 5%;
}

.hero {
  text-align: center;
  padding: 4rem 0;
  color: white;
}

.hero-title {
  font-size: 3rem;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.hero-subtitle {
  font-size: 1.25rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.btn-primary {
  display: inline-block;
  padding: 0.75rem 2rem;
  background: white;
  color: #667eea;
  text-decoration: none;
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.features {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  margin: 2rem 0;
}

.section-title {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  color: #333;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.feature-card {
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 0.75rem;
  text-align: center;
}

.feature-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  margin-bottom: 0.5rem;
  color: #333;
}

.feature-card p {
  color: #666;
  font-size: 0.9rem;
}

.preview {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  margin: 2rem 0;
}

.preview-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.preview-item {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
}

.preview-question {
  color: #333;
}

.footer {
  text-align: center;
  padding: 1.5rem;
  color: white;
  opacity: 0.8;
}
</style>
