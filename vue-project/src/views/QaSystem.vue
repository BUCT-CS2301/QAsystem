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
                  <button v-for="tag in suggestionTags" :key="tag.name" @click="handleTypeClick(tag)" class="suggestion-tag">
                    {{ tag.name }}
                  </button>
                </div>
              </div>
            </div>

            <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.type]">
              <div class="message-content">
                <p v-if="msg.content">{{ msg.content }}</p>
                <div v-if="msg.hasLink" class="try-link">
                  <a href="#" @click.prevent="handleTryLink(msg.linkExample)" class="try-link-text">{{ msg.linkText }}</a>
                </div>
                <div v-if="msg.llmContent" class="llm-content">
                  <span v-html="formatMarkdown(msg.llmContent)"></span>
                </div>
                <div v-if="msg.images && msg.images.length > 0" class="images">
                  <div class="image-label">🖼️ 相关图片：</div>
                  <div class="image-list">
                    <img v-for="(img, iIndex) in msg.images" :key="iIndex" :src="img.url" class="chat-image" @click="previewImage(img.url)" />
                  </div>
                </div>
                <div v-if="msg.sources && msg.sources.length > 0" class="sources">
                  <div class="source-label">📚 数据来源：</div>
                  <div v-for="(source, sIndex) in msg.sources" :key="sIndex" class="source-item">
                    <a :href="source.url" target="_blank" class="source-link">{{ source.name }}</a>
                  </div>
                </div>
                <div v-if="msg.noData" class="no-data">
                  <span class="no-data-icon">⚠️</span>
                  <span>暂无相关数据</span>
                </div>
              </div>
            </div>

            <div v-if="isLoading" class="loading-message">
              <div class="loading-spinner"></div>
              <p>正在思考中...</p>
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
              <div v-for="(type, index) in questionTypes" :key="index" @click="handleTypeClick(type)" class="type-item">
                <span class="type-icon">{{ type.icon }}</span>
                <span class="type-text">{{ type.name }}</span>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </main>

    <div v-if="previewImageUrl" class="image-preview" @click="previewImageUrl = null">
      <img :src="previewImageUrl" class="preview-image" />
      <span class="close-preview">✕</span>
    </div>

    <footer class="footer">
      <p>&copy; 2026 文物知识问答系统 - 基于知识图谱与大语言模型构建</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue';

const question = ref('');
const messages = ref([]);
const isLoading = ref(false);
const messagesContainer = ref(null);
const previewImageUrl = ref(null);
const abortController = ref(null);

const questionTypes = [
  { icon: '🏛️', name: '文物收藏地', example: '《清明上河图》现藏于哪家博物馆？' },
  { icon: '📅', name: '文物年代', example: '司母戊鼎是什么时期的文物？' },
  { icon: '🔨', name: '文物材质', example: '青花瓷是什么材质制成的？' },
  { icon: '🏺', name: '文物类型', example: '兵马俑属于什么类型的文物？' },
  { icon: '📝', name: '文物介绍', example: '请介绍一下《兰亭序》' },
  { icon: '✍️', name: '书画作者', example: '《富春山居图》的作者是谁？' },
  { icon: '👤', name: '作者生平', example: '王羲之的生平经历是怎样的？' },
  { icon: '📜', name: '同一作者作品', example: '与《清明上河图》同一作者的作品有哪些？' },
  { icon: '🏯', name: '同一朝代文物', example: '唐代有哪些代表性文物？' },
  { icon: '📏', name: '尺寸规格', example: '曾侯乙编钟的尺寸规格是多少？' },
  { icon: '🔗', name: '相关文物推荐', example: '与《千里江山图》相关的文物有哪些？' }
];

const suggestionTags = questionTypes.slice(0, 8).map(item => ({ name: item.name, example: item.example }));

const faqs = [
  { question: '《清明上河图》现藏于哪家博物馆？' },
  { question: '青花瓷属于哪个历史时期的代表性文物？' },
  { question: '司母戊鼎是什么材质制成的？' },
  { question: '《兰亭序》的作者是谁？' },
  { question: '唐代有哪些代表性文物？' },
  { question: '与《富春山居图》风格相似的文物有哪些？' }
];



const formatMarkdown = (text) => {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br />');
};

const submitQuestion = async () => {
  if (!question.value.trim() || isLoading.value) return;

  const userQuestion = question.value.trim();
  messages.value.push({ type: 'user', content: userQuestion });
  question.value = '';
  isLoading.value = true;

  const botMessage = {
    type: 'bot',
    llmContent: '',
    sources: [],
    images: [],
    noData: false
  };
  messages.value.push(botMessage);
  const messageIndex = messages.value.length - 1;

  await nextTick(() => {
    scrollToBottom();
  });

  abortController.value = new AbortController();

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
      },
      body: JSON.stringify({ question: userQuestion }),
      signal: abortController.value.signal
    });

    if (!response.ok) {
      throw new Error('请求失败');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let currentEvent = null;

    let eventData = [];

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (line === '') {
          if (currentEvent && eventData.length > 0) {
            const dataStr = eventData.join('\n');
            switch (currentEvent) {
              case 'llm':
                messages.value[messageIndex].llmContent += dataStr;
                nextTick(() => scrollToBottom());
                break;
              case 'source':
                try {
                  const source = JSON.parse(dataStr);
                  // 顺便前端也做个去重，防止相同链接被渲染多次
                  if (!messages.value[messageIndex].sources.some(s => s.url === source.url)) {
                    messages.value[messageIndex].sources.push(source);
                  }
                } catch (e) {
                  console.error('解析 source 失败:', e);
                }
                break;
              case 'img':
                try {
                  const img = JSON.parse(dataStr);
                  messages.value[messageIndex].images.push(img);
                } catch (e) {
                  console.error('解析 img 失败:', e);
                }
                break;
              case 'done':
                if (!messages.value[messageIndex].llmContent && 
                    messages.value[messageIndex].sources.length === 0 && 
                    messages.value[messageIndex].images.length === 0) {
                  messages.value[messageIndex].noData = true;
                }
                break;
              case 'error':
                console.error('服务端错误:', dataStr);
                messages.value[messageIndex].noData = true;
                break;
            }
          }
          currentEvent = null;
          eventData = [];
          continue;
        }

        if (line.startsWith('event:')) {
          currentEvent = line.slice(6).trim();
        } else if (line.startsWith('data:')) {
          let val = line.slice(5);
          if (val.startsWith(' ')) val = val.slice(1);
          eventData.push(val);
        }
      }
    }
  } catch (error) {
    if (error.name !== 'AbortError') {
      console.error('请求异常:', error);
      messages.value[messageIndex].noData = true;
    }
  } finally {
    isLoading.value = false;
    abortController.value = null;
    await nextTick(() => scrollToBottom());
  }
};

const handleQuickQuestion = (q) => {
  question.value = q;
  submitQuestion();
};

const handleTypeClick = (type) => {
  messages.value.push({
    type: 'bot',
    content: `您可以这样问："${type.example}"`,
    hasLink: true,
    linkText: '去试试',
    linkExample: type.example,
    llmContent: '',
    sources: [],
    images: []
  });
  nextTick(() => {
    scrollToBottom();
  });
};

const handleTryLink = (example) => {
  question.value = example;
};

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const previewImage = (url) => {
  previewImageUrl.value = url;
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

.llm-content {
  white-space: pre-wrap;
  word-wrap: break-word;
}

.llm-content strong {
  font-weight: 600;
}

.llm-content em {
  font-style: italic;
}

.images {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.image-label {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.image-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.chat-image {
  max-width: 150px;
  max-height: 150px;
  object-fit: cover;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.chat-image:hover {
  transform: scale(1.05);
}

.image-preview {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  cursor: pointer;
}

.preview-image {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
  border-radius: 0.5rem;
}

.close-preview {
  position: absolute;
  top: 2rem;
  right: 2rem;
  font-size: 2rem;
  color: white;
  cursor: pointer;
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

.try-link {
  margin-top: 0.75rem;
}

.try-link-text {
  font-size: 0.9rem;
  color: #667eea;
  text-decoration: none;
  padding: 0.375rem 0.75rem;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 0.25rem;
  transition: all 0.3s ease;
}

.try-link-text:hover {
  background: rgba(102, 126, 234, 0.2);
  text-decoration: underline;
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
  width: 420px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  overflow-y: auto;
  scrollbar-width: none;
}

.sidebar::-webkit-scrollbar {
  display: none;
}

.sidebar-section {
  background: white;
  border-radius: 1rem;
  padding: 0.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transform: scale(0.95);
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
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.type-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.type-item:hover {
  background: #e9ecef;
  transform: translateY(-2px);
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
