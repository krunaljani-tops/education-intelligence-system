import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, User, Sparkles, Database, Code, CornerDownLeft } from 'lucide-react';
import { chatService } from '../services/api';

const QUICK_PROMPTS = [
  "How many students are available in the dataset?",
  "Which course has the highest enrollment?",
  "Which course has the lowest enrollment?",
  "How many students have dropped their enrollment?",
  "Show students with attendance below 75%.",
  "Which batch has the lowest attendance?",
  "What is the average assessment score?",
  "Which course has the highest assessment performance?",
  "How many assessments are missing?",
  "What is the total collected fee amount?",
  "How much payment is pending?",
  "Which payment method is most frequently used?",
  "Give me the top five academic improvement recommendations.",
  "Identify major operational problems in the institute."
];

export const AIAssistant = () => {
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      text: "Hello! I am your AI Education Business Intelligence Assistant. I am directly connected to the PostgreSQL database and multi-agent analysis results for '02_Education.xlsx'. Ask me any question regarding students, courses, attendance, examination scores, fee collections, or operational bottlenecks.",
      query: null
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (queryText = input) => {
    if (!queryText.trim()) return;

    const userMessage = { sender: 'user', text: queryText };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const history = messages.map(m => ({ sender: m.sender, text: m.text }));
      const res = await chatService.ask(queryText, history);
      
      const botMessage = {
        sender: 'assistant',
        text: res.answer,
        query: res.evidence_query,
        data: res.calculated_data
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, {
        sender: 'assistant',
        text: "I encountered an error querying the backend intelligence engine. Please ensure the backend server is running.",
        query: null
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto flex flex-col h-[calc(100vh-140px)]">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight flex items-center space-x-2">
          <Bot className="w-5 h-5 text-brand-600" />
          <span>AI Education Assistant</span>
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Ask questions against actual PostgreSQL records and verified agent intelligence outputs.
        </p>
      </div>

      {/* Suggested Prompts Carousel */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-2 scrollbar-none">
        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider shrink-0 flex items-center space-x-1">
          <Sparkles className="w-3 h-3 text-brand-600" />
          <span>Suggestions:</span>
        </span>
        {QUICK_PROMPTS.map((prompt, i) => (
          <button
            key={i}
            onClick={() => handleSend(prompt)}
            className="text-xs shrink-0 px-3 py-1 bg-white hover:bg-brand-50 hover:text-brand-700 hover:border-brand-200 text-slate-600 border border-slate-200/80 rounded-full transition-colors whitespace-nowrap shadow-2xs"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Chat Messages Log */}
      <div className="flex-1 bg-white rounded-2xl border border-slate-200/80 shadow-sm p-4 overflow-y-auto space-y-4">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex items-start space-x-3 ${m.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}
          >
            <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
              m.sender === 'user' ? 'bg-brand-600 text-white' : 'bg-slate-100 text-brand-600'
            }`}>
              {m.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-xs leading-relaxed ${
              m.sender === 'user'
                ? 'bg-brand-600 text-white shadow-sm'
                : 'bg-slate-50 text-slate-800 border border-slate-100 shadow-2xs'
            }`}>
              <div className="whitespace-pre-wrap">{m.text}</div>

              {m.query && (
                <div className="mt-2.5 pt-2 border-t border-slate-200/60 text-[11px] font-mono text-slate-500 flex items-start space-x-1.5">
                  <Code className="w-3.5 h-3.5 text-brand-500 shrink-0 mt-0.5" />
                  <span className="break-all">{m.query}</span>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center space-x-3 text-xs text-slate-400">
            <div className="w-8 h-8 rounded-xl bg-slate-100 flex items-center justify-center text-brand-600">
              <Bot className="w-4 h-4" />
            </div>
            <div className="flex items-center space-x-1.5 bg-slate-50 border border-slate-100 px-4 py-2.5 rounded-2xl">
              <div className="w-1.5 h-1.5 bg-brand-500 rounded-full animate-bounce" />
              <div className="w-1.5 h-1.5 bg-brand-500 rounded-full animate-bounce [animation-delay:0.2s]" />
              <div className="w-1.5 h-1.5 bg-brand-500 rounded-full animate-bounce [animation-delay:0.4s]" />
              <span className="text-[11px] text-slate-500 ml-1">Analyzing database records...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input */}
      <div className="bg-white rounded-2xl p-2 border border-slate-200/80 shadow-sm flex items-center space-x-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question (e.g. 'How much payment is pending?')..."
          className="flex-1 text-xs px-3 py-2.5 bg-transparent focus:outline-none text-slate-800 placeholder-slate-400"
        />
        <button
          onClick={() => handleSend()}
          disabled={!input.trim() || loading}
          className="p-2.5 bg-brand-600 hover:bg-brand-700 disabled:opacity-40 text-white rounded-xl shadow-sm transition-colors"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
