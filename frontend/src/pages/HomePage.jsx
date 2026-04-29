import { useState } from 'react'
import { useApp } from '../store/index.jsx'

export default function HomePage() {
  const { selectKB } = useApp()

  const features = [
    {
      icon: '📚',
      title: '多知识库管理',
      description: '创建和管理多个知识库，分类存储不同领域的文档'
    },
    {
      icon: '🔍',
      title: '混合检索策略',
      description: '结合向量检索和BM25关键词检索，提升召回精度'
    },
    {
      icon: '🎯',
      title: 'Rerank重排序',
      description: '使用BGE-Reranker对检索结果进行精细排序'
    },
    {
      icon: '💬',
      title: '智能对话',
      description: '基于文档内容进行问答，答案可追溯到原始来源'
    },
    {
      icon: '📄',
      title: '多格式支持',
      description: '支持PDF、TXT、Markdown、DOC等常见文档格式'
    },
    {
      icon: '🚀',
      title: '一键部署',
      description: '支持Render、Vercel等免费平台部署，公网可访问'
    }
  ]

  const techStack = [
    { name: 'React', desc: '前端框架' },
    { name: 'Flask', desc: '后端框架' },
    { name: 'Chroma', desc: '向量数据库' },
    { name: 'BGE', desc: '中文Embedding' },
    { name: 'SQLite', desc: '关系数据库' },
    { name: '通义千问', desc: 'LLM大模型' }
  ]

  return (
    <div className="chat-container">
      <div style={{
        textAlign: 'center',
        padding: '60px 0 40px',
        background: 'linear-gradient(180deg, var(--bg-tertiary) 0%, transparent 100%)',
        borderRadius: '0 0 24px 24px',
        marginBottom: 48
      }}>
        <div style={{ fontSize: 64, marginBottom: 24 }}>🤖</div>
        <h1 style={{
          fontSize: 36,
          fontWeight: 700,
          background: 'linear-gradient(135deg, var(--accent), #a78bfa)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          marginBottom: 16
        }}>
          RAG 智能问答系统
        </h1>
        <p style={{
          fontSize: 18,
          color: 'var(--text-secondary)',
          maxWidth: 600,
          margin: '0 auto',
          lineHeight: 1.6
        }}>
          基于检索增强生成（RAG）技术的智能问答平台，
          支持文档上传、语义搜索、混合检索和AI回答生成
        </p>

        <div style={{ marginTop: 32, display: 'flex', gap: 16, justifyContent: 'center' }}>
          <button
            onClick={() => selectKB({ id: 1, name: '示例知识库' })}
            className="btn btn-primary"
            style={{ padding: '12px 32px', fontSize: 16 }}
          >
            快速开始 →
          </button>
        </div>
      </div>

      <div style={{ marginBottom: 48 }}>
        <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 24, textAlign: 'center' }}>
          核心功能
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: 16
        }}>
          {features.map((feature, idx) => (
            <div
              key={idx}
              className="card"
              style={{
                padding: 24,
                transition: 'transform 0.2s, box-shadow 0.2s',
                cursor: 'default'
              }}
            >
              <div style={{ fontSize: 32, marginBottom: 16 }}>{feature.icon}</div>
              <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>{feature.title}</h3>
              <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: 48 }}>
        <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 24, textAlign: 'center' }}>
          技术栈
        </h2>
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: 12,
          justifyContent: 'center'
        }}>
          {techStack.map((tech, idx) => (
            <div
              key={idx}
              style={{
                padding: '12px 24px',
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border)',
                borderRadius: 24,
                display: 'flex',
                alignItems: 'center',
                gap: 12
              }}
            >
              <span style={{ fontWeight: 600, color: 'var(--accent)' }}>{tech.name}</span>
              <span style={{ color: 'var(--text-muted)' }}>{tech.desc}</span>
            </div>
          ))}
        </div>
      </div>

      <div style={{
        padding: 32,
        background: 'var(--bg-secondary)',
        borderRadius: 16,
        border: '1px solid var(--border)',
        textAlign: 'center'
      }}>
        <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12 }}>🚀 快速部署</h3>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 16 }}>
          项目支持一键部署到 Render、Vercel、Hugging Face Spaces 等免费平台
        </p>
        <div style={{ fontFamily: 'monospace', fontSize: 13, color: 'var(--text-secondary)' }}>
          <p style={{ marginBottom: 8 }}>详细部署教程请参考项目文档</p>
        </div>
      </div>

      <div style={{ marginTop: 48, textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
        <p>RAG 智能问答系统 v1.0.0 · 基于 Flask + React 构建</p>
      </div>
    </div>
  )
}
