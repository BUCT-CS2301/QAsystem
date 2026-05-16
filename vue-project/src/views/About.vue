<template>
  <div class="about-container">
    <header class="header">
      <div class="logo">
        <span class="logo-icon">🏺</span>
        <span class="logo-text">文物知识问答系统</span>
      </div>
      <nav class="nav">
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link to="/qa" class="nav-link">知识问答</router-link>
        <router-link to="/about" class="nav-link active">关于系统</router-link>
      </nav>
    </header>

    <main class="main-content">
      <section class="about-section">
        <h1 class="section-title">关于系统</h1>
        <p class="section-intro">本系统是基于知识图谱与大语言模型构建的文物知识问答服务平台，旨在为用户提供准确、可靠的文物知识查询服务。</p>
      </section>

      <section class="architecture-section">
        <h2 class="section-title">系统架构</h2>
        <div class="architecture-diagram">
          <div class="arch-layer">
            <div class="layer-title">用户层</div>
            <div class="layer-desc">自然语言输入界面</div>
          </div>
          <div class="arch-arrow">↓</div>
          <div class="arch-layer">
            <div class="layer-title">意图识别层</div>
            <div class="layer-desc">实体抽取与意图分类</div>
          </div>
          <div class="arch-arrow">↓</div>
          <div class="arch-layer">
            <div class="layer-title">知识检索层</div>
            <div class="layer-desc">SPARQL/Cypher查询</div>
          </div>
          <div class="arch-arrow">↓</div>
          <div class="arch-layer">
            <div class="layer-title">知识图谱</div>
            <div class="layer-desc">文物知识数据存储</div>
          </div>
          <div class="arch-arrow">↑</div>
          <div class="arch-layer">
            <div class="layer-title">语言生成层</div>
            <div class="layer-desc">大语言模型回答生成</div>
          </div>
          <div class="arch-arrow">↑</div>
          <div class="arch-layer">
            <div class="layer-title">结果展示层</div>
            <div class="layer-desc">答案溯源与可信度展示</div>
          </div>
        </div>
      </section>

      <section class="features-section">
        <h2 class="section-title">功能特点</h2>
        <div class="features-grid">
          <div class="feature-item">
            <div class="feature-icon">✅</div>
            <h3>事实准确性</h3>
            <p>基于知识图谱数据，确保回答的准确性，避免大模型幻觉问题</p>
          </div>
          <div class="feature-item">
            <div class="feature-icon">🔗</div>
            <h3>答案溯源</h3>
            <p>每条回答附带数据来源说明和原始数据链接，增强可信度</p>
          </div>
          <div class="feature-item">
            <div class="feature-icon">💡</div>
            <h3>智能推理</h3>
            <p>支持从简单属性查询到复杂关系推理的多层次问答</p>
          </div>
          <div class="feature-item">
            <div class="feature-icon">🎯</div>
            <h3>意图识别</h3>
            <p>自动识别用户问题意图，精确匹配知识图谱查询</p>
          </div>
        </div>
      </section>

      <section class="coverage-section">
        <h2 class="section-title">问答覆盖范围</h2>
        <div class="coverage-list">
          <div class="coverage-item">🏛️ 文物收藏地查询</div>
          <div class="coverage-item">📅 文物年代查询</div>
          <div class="coverage-item">🔨 文物材质查询</div>
          <div class="coverage-item">🏺 文物类型查询</div>
          <div class="coverage-item">📝 文物介绍</div>
          <div class="coverage-item">✍️ 书画作者查询</div>
          <div class="coverage-item">👤 作者生平查询</div>
          <div class="coverage-item">🎨 同一作者作品</div>
          <div class="coverage-item">👑 同一朝代文物</div>
          <div class="coverage-item">📐 文物尺寸规格</div>
          <div class="coverage-item">🔗 相关文物推荐</div>
        </div>
      </section>
    </main>

    <footer class="footer">
      <p>&copy; 2024 文物知识问答系统 - 基于知识图谱与大语言模型构建</p>
    </footer>
  </div>
</template>

<style scoped>
.about-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 5%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  font-size: 1.75rem;
  margin-bottom: 1rem;
  color: #333;
  border-bottom: 2px solid #667eea;
  padding-bottom: 0.5rem;
}

.section-intro {
  font-size: 1.1rem;
  color: #666;
  line-height: 1.6;
}

.about-section,
.architecture-section,
.features-section,
.coverage-section {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.architecture-diagram {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.arch-layer {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem 2rem;
  border-radius: 0.5rem;
  text-align: center;
  min-width: 200px;
}

.layer-title {
  color: white;
  font-weight: 600;
}

.layer-desc {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.arch-arrow {
  color: #667eea;
  font-size: 1.5rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.feature-item {
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 0.75rem;
}

.feature-icon {
  font-size: 2rem;
  margin-bottom: 0.75rem;
}

.feature-item h3 {
  margin-bottom: 0.5rem;
  color: #333;
}

.feature-item p {
  color: #666;
  font-size: 0.9rem;
  line-height: 1.5;
}

.coverage-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.coverage-item {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
  color: #333;
}

.footer {
  text-align: center;
  padding: 1.5rem;
  background: #333;
  color: white;
}
</style>
