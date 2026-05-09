<template>
  <div class="qa-container">
    <header class="header">
      <div class="logo">
        <span class="logo-icon">🏺</span>
        <span class="logo-text">文物知识问答系统</span>
      </div>
      <nav class="nav">
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link to="/qa" class="nav-link active">知识问答</router-link>
        <router-link to="/about" class="nav-link">关于系统</router-link>
      </nav>
    </header>

    <main class="main-content">
      <div class="qa-wrapper">
        <div class="chat-container">
          <div class="chat-header">
            <h2>智能问答</h2>
            <p class="header-desc">基于知识图谱与大语言模型的文物知识问答</p>
          </div>

          <div class="chat-messages" ref="messagesContainer">
            <div class="message welcome-message">
              <div class="message-content">
                <p>您好！我是文物知识问答助手，请问有什么可以帮助您的？</p>
                <p class="suggestions">您可以尝试询问：</p>
                <div class="suggestion-tags">
                  <button v-for="tag in suggestionTags" :key="tag" @click="handleQuickQuestion(tag)" class="suggestion-tag">
                    {{ tag }}
                  </button>
                </div>
              </div>
            </div>

            <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.type]">
              <div class="message-content">
                <p>{{ msg.content }}</p>
                <div v-if="msg.sources && msg.sources.length > 0" class="sources">
                  <div class="source-label">📚 数据来源：</div>
                  <div v-for="(source, sIndex) in msg.sources" :key="sIndex" class="source-item">
                    <a :href="source.url" target="_blank" class="source-link">{{ source.name }}</a>
                  </div>
                </div>
                <div v-if="msg.llmContent" class="llm-note">
                  <span class="llm-badge">AI补充</span>
                  <span>{{ msg.llmContent }}</span>
                </div>
                <div v-if="msg.noData" class="no-data">
                  <span class="no-data-icon">⚠️</span>
                  <span>暂无相关数据</span>
                </div>
              </div>
            </div>

            <div v-if="isLoading" class="loading-message">
              <div class="loading-spinner"></div>
              <p>正在检索知识图谱...</p>
            </div>
          </div>

          <div class="input-container">
            <input 
              v-model="question" 
              @keyup.enter="submitQuestion" 
              type="text" 
              placeholder="请输入您的问题..." 
              class="question-input"
              :disabled="isLoading"
            />
            <button @click="submitQuestion" class="submit-btn" :disabled="isLoading || !question.trim()">
              <span class="send-icon">➤</span>
            </button>
          </div>
        </div>

        <aside class="sidebar">
          <div class="sidebar-section">
            <h3>常见问题</h3>
            <div class="faq-list">
              <div v-for="(faq, index) in faqs" :key="index" @click="handleQuickQuestion(faq.question)" class="faq-item">
                <span class="faq-icon">▶</span>
                <span class="faq-text">{{ faq.question }}</span>
              </div>
            </div>
          </div>

          <div class="sidebar-section">
            <h3>问答类型</h3>
            <div class="type-list">
              <div v-for="(type, index) in questionTypes" :key="index" class="type-item">
                <span class="type-icon">{{ type.icon }}</span>
                <span class="type-text">{{ type.name }}</span>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </main>

    <footer class="footer">
      <p>&copy; 2024 文物知识问答系统 - 基于知识图谱与大语言模型构建</p>
    </footer>
  </div>
</template>

<script setup>import { ref, nextTick } from 'vue';
const question = ref('');
const messages = ref([]);
const isLoading = ref(false);
const messagesContainer = ref(null);
const suggestionTags = [
 '文物收藏地',
 '文物年代',
 '文物材质',
 '文物类型',
 '文物介绍',
 '书画作者',
 '作者生平',
 '相关文物'
];
const faqs = [
 { question: '《清明上河图》现藏于哪家博物馆？', type: '收藏地' },
 { question: '青花瓷属于哪个历史时期的代表性文物？', type: '年代' },
 { question: '司母戊鼎是什么材质制成的？', type: '材质' },
 { question: '《兰亭序》的作者是谁？', type: '作者' },
 { question: '唐代有哪些代表性文物？', type: '朝代' },
 { question: '与《富春山居图》风格相似的文物有哪些？', type: '推荐' }
];
const questionTypes = [
 { icon: '🏛️', name: '文物收藏地' },
 { icon: '📅', name: '文物年代' },
 { icon: '🔨', name: '文物材质' },
 { icon: '🏺', name: '文物类型' },
 { icon: '📝', name: '文物介绍' },
 { icon: '✍️', name: '书画作者' },
 { icon: '👤', name: '作者生平' },
 { icon: '🎨', name: '同一作者作品' },
 { icon: '👑', name: '同一朝代文物' },
 { icon: '📐', name: '尺寸规格' },
 { icon: '🔗', name: '相关文物推荐' }
];
const mockAnswers = {
 '文物收藏地': {
 content: '根据知识图谱数据，该文物现藏于北京故宫博物院。',
 sources: [
 { name: '故宫博物院官网', url: 'https://www.dpm.org.cn/' }
 ]
 },
 '文物年代': {
 content: '该文物属于唐代（公元618年-907年）。',
 sources: [
 { name: '中国国家博物馆', url: 'https://www.chnmuseum.cn/' }
 ],
 llmContent: '唐代是中国历史上文化艺术高度繁荣的时期，这一时期的文物具有鲜明的时代特征。'
 },
 '文物材质': {
 content: '该文物由青铜铸造而成。',
 sources: [
 { name: '上海博物馆', url: 'https://www.shanghaimuseum.net/' }
 ]
 },
 '文物类型': {
 content: '该文物属于青铜器类别，具体为礼器。',
 sources: [
 { name: '青铜器数据库', url: 'https://www.bronze-age.cn/' }
 ]
 },
 '文物介绍': {
 content: '这件文物是一件精美的唐代青花瓷瓶，高35厘米，口径12厘米，造型端庄典雅，纹饰精美繁复。',
 sources: [
 { name: '大英博物馆', url: 'https://www.britishmuseum.org/' },
 { name: '大都会艺术博物馆', url: 'https://www.metmuseum.org/' }
 ],
 llmContent: '青花瓷是中国瓷器中的经典品类，以钴料在白瓷上绘制图案，经高温烧成后呈现出独特的蓝色花纹。'
 },
 '书画作者': {
 content: '《兰亭序》的作者是东晋书法家王羲之。',
 sources: [
 { name: '故宫博物院书画馆', url: 'https://www.dpm.org.cn/collection/painting' }
 ],
 llmContent: '王羲之被誉为"书圣"，其书法风格飘逸灵动，对后世书法发展产生了深远影响。'
 },
 '作者生平': {
 content: '王羲之（303年-361年），字逸少，琅琊临沂人，东晋时期著名书法家。',
 sources: [
 { name: '中国书法网', url: 'https://www.chinacalligraphy.org/' }
 ],
 llmContent: '王羲之在书法艺术上造诣极高，其代表作《兰亭序》被称为"天下第一行书"。'
 },
 '同一作者作品': {
 content: '王羲之的其他著名作品包括《快雪时晴帖》、《十七帖》、《姨母帖》等。',
 sources: [
 { name: '台北故宫博物院', url: 'https://www.npm.edu.tw/' }
 ]
 },
 '同一朝代文物': {
 content: '唐代代表性文物包括唐三彩、青铜镜、金银器、壁画等。',
 sources: [
 { name: '陕西历史博物馆', url: 'https://www.sxhm.com/' },
 { name: '敦煌研究院', url: 'https://www.dha.ac.cn/' }
 ]
 },
 '尺寸规格': {
 content: '该文物高45厘米，宽28厘米，重约15公斤。',
 sources: [
 { name: '文物数据平台', url: 'https://www.culturalchina.com/' }
 ]
 },
 '相关文物': {
 content: '与该文物风格相似的文物包括《千里江山图》、《富春山居图》、《溪山行旅图》等。',
 sources: [
 { name: '故宫博物院', url: 'https://www.dpm.org.cn/' },
 { name: '辽宁省博物馆', url: 'https://www.lnmuseum.com/' }
 ],
 llmContent: '这些作品均属于中国传统山水画的经典之作，展现了中国古代绘画艺术的高超水平。'
 }
};
const getAnswer = (q) => {
 const lowerQ = q.toLowerCase();
 if (lowerQ.includes('收藏') || lowerQ.includes('博物馆')) {
 return mockAnswers['文物收藏地'];
 }
 else if (lowerQ.includes('年代') || lowerQ.includes('时期') || lowerQ.includes('朝代')) {
 if (lowerQ.includes('有哪些') || lowerQ.includes('哪些')) {
 return mockAnswers['同一朝代文物'];
 }
 return mockAnswers['文物年代'];
 }
 else if (lowerQ.includes('材质') || lowerQ.includes('材料') || lowerQ.includes('什么做的')) {
 return mockAnswers['文物材质'];
 }
 else if (lowerQ.includes('类型') || lowerQ.includes('类别') || lowerQ.includes('属于哪种')) {
 return mockAnswers['文物类型'];
 }
 else if (lowerQ.includes('介绍') || lowerQ.includes('描述')) {
 return mockAnswers['文物介绍'];
 }
 else if (lowerQ.includes('作者') && !lowerQ.includes('生平')) {
 if (lowerQ.includes('作品') || lowerQ.includes('还有哪些')) {
 return mockAnswers['同一作者作品'];
 }
 return mockAnswers['书画作者'];
 }
 else if (lowerQ.includes('生平') || lowerQ.includes('经历')) {
 return mockAnswers['作者生平'];
 }
 else if (lowerQ.includes('尺寸') || lowerQ.includes('规格') || lowerQ.includes('重量')) {
 return mockAnswers['尺寸规格'];
 }
 else if (lowerQ.includes('相似') || lowerQ.includes('推荐') || lowerQ.includes('相关')) {
 return mockAnswers['相关文物'];
 }
 else {
 return null;
 }
};
const submitQuestion = async () => {
 if (!question.value.trim() || isLoading.value)
 return;
 const userQuestion = question.value.trim();
 messages.value.push({ type: 'user', content: userQuestion });
 question.value = '';
 isLoading.value = true;
 await nextTick(() => {
 scrollToBottom();
 });
 await new Promise(resolve => setTimeout(resolve, 1500));
 const answer = getAnswer(userQuestion);
 if (answer) {
 messages.value.push({
 type: 'bot',
 content: answer.content,
 sources: answer.sources,
 llmContent: answer.llmContent
 });
 }
 else {
 messages.value.push({
 type: 'bot',
 content: '',
 noData: true
 });
 }
 isLoading.value = false;
 await nextTick(() => {
 scrollToBottom();
 });
};
const handleQuickQuestion = (q) => {
 question.value = q;
 submitQuestion();
};
const scrollToBottom = () => {
 if (messagesContainer.value) {
 messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
 }
};
</script>

<style scoped>
.qa-container {
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
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
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
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.qa-wrapper {
  display: flex;
  gap: 2rem;
  height: calc(100vh - 200px);
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.chat-header {
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.chat-header h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
}

.header-desc {
  margin: 0;
  opacity: 0.9;
  font-size: 0.9rem;
}

.chat-messages {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.message {
  max-width: 80%;
}

.message.user {
  align-self: flex-end;
}

.message.bot {
  align-self: flex-start;
}

.message.welcome-message {
  align-self: center;
  max-width: 100%;
}

.message-content {
  padding: 1rem 1.5rem;
  border-radius: 1rem;
  line-height: 1.6;
}

.message.user .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 0.25rem;
}

.message.bot .message-content {
  background: #f1f3f4;
  color: #333;
  border-bottom-left-radius: 0.25rem;
}

.welcome-message .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
}

.suggestions {
  margin-top: 1rem;
  font-size: 0.9rem;
  opacity: 0.9;
}

.suggestion-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
  justify-content: center;
}

.suggestion-tag {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 2rem;
  color: white;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.3s ease;
}

.suggestion-tag:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.sources {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.source-label {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.source-item {
  margin-bottom: 0.3rem;
}

.source-link {
  font-size: 0.85rem;
  color: #667eea;
  text-decoration: none;
  transition: color 0.3s ease;
}

.source-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

.llm-note {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #fff3cd;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.llm-badge {
  background: #ffc107;
  color: #333;
  padding: 0.2rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.7rem;
  font-weight: 600;
  flex-shrink: 0;
}

.no-data {
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: #f8d7da;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #721c24;
}

.loading-message {
  align-self: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: #666;
}

.loading-spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.input-container {
  padding: 1rem 1.5rem;
  border-top: 1px solid #eee;
  display: flex;
  gap: 1rem;
}

.question-input {
  flex: 1;
  padding: 0.875rem 1.25rem;
  border: 2px solid #e0e0e0;
  border-radius: 2rem;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.question-input:focus {
  outline: none;
  border-color: #667eea;
}

.question-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.submit-btn {
  padding: 0.875rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 2rem;
  color: white;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.send-icon {
  font-size: 1.2rem;
}

.sidebar {
  width: 320px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.sidebar-section {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.sidebar-section h3 {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  color: #333;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #f0f0f0;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.faq-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.faq-item:hover {
  background: #f0f0f0;
  transform: translateX(4px);
}

.faq-icon {
  color: #667eea;
  font-size: 0.8rem;
}

.faq-text {
  font-size: 0.9rem;
  color: #333;
  line-height: 1.4;
}

.type-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.type-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
}

.type-icon {
  font-size: 1.2rem;
}

.type-text {
  font-size: 0.85rem;
  color: #333;
}

.footer {
  text-align: center;
  padding: 1.5rem;
  background: #333;
  color: white;
}

@media (max-width: 900px) {
  .qa-wrapper {
    flex-direction: column;
    height: auto;
  }
  
  .sidebar {
    width: 100%;
  }
  
  .chat-messages {
    max-height: 50vh;
  }
  
  .message {
    max-width: 95%;
  }
}
</style>
