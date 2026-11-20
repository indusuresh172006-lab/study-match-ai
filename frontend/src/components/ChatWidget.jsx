import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import api from "../api";

function ChatWidget({ user }) {
  const [isOpen, setIsOpen] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [suggestedChips, setSuggestedChips] = useState([
    "What entrance exams should I prepare for?",
    "Which courses match my skill profile?",
    "How can I improve my weak topics?",
    "Tell me about scholarships in India.",
  ]);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) {
      initSession();
    }
  }, [isOpen]);

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, sending, isOpen]);

  const initSession = async () => {
    try {
      // Check existing sessions
      const res = await api.get("/api/v1/chat/sessions");
      if (res.data && res.data.length > 0) {
        const latest = res.data[0];
        setSessionId(latest.session_id);
        fetchMessages(latest.session_id);
      } else {
        // Create new session
        const newSess = await api.post("/api/v1/chat/sessions", {
          title: "Quick Guidance Chat",
        });
        setSessionId(newSess.data.session_id);
        setMessages([
          {
            id: 1,
            sender: "bot",
            message: `Hello ${user?.name || "Student"}! 👋 I am your FLINT Assistant. Ask me anything about syllabus topics, entrance exams, courses, colleges, or your skill profile!`,
          },
        ]);
      }
    } catch (err) {
      console.error("Init chat session error:", err);
    }
  };

  const fetchMessages = async (sId) => {
    try {
      const res = await api.get(`/api/v1/chat/sessions/${sId}/messages`);
      if (res.data && res.data.length > 0) {
        setMessages(res.data);
      } else {
        setMessages([
          {
            id: 1,
            sender: "bot",
            message: `Hello ${user?.name || "Student"}! 👋 I am your FLINT Assistant. How can I help you today?`,
          },
        ]);
      }
    } catch (err) {
      console.error("Fetch chat messages error:", err);
    }
  };

  const handleSendMessage = async (customText) => {
    const textToSend = customText || inputMessage;
    if (!textToSend.trim() || sending) return;

    if (!sessionId) {
      await initSession();
    }

    const tempUserMsg = {
      id: Date.now(),
      sender: "student",
      message: textToSend,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMsg]);
    setInputMessage("");
    setSending(true);

    try {
      const res = await api.post(`/api/v1/chat/sessions/${sessionId}/message`, {
        message: textToSend,
      });

      const botMsg = {
        id: Date.now() + 1,
        sender: "bot",
        message: res.data.bot_response,
        sources: res.data.sources,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, botMsg]);
      if (res.data.suggested_questions?.length > 0) {
        setSuggestedChips(res.data.suggested_questions);
      }
    } catch (err) {
      console.error("Send message error:", err);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 2,
          sender: "bot",
          message: "I am having trouble connecting to the mentoring engine right now. Please try again shortly.",
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <>
      {/* Floating Action Pill */}
      <button
        className="floating-chat-trigger"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Open FLINT Assistant"
      >
        <span className="trigger-icon">{isOpen ? "✕" : "🤖"}</span>
        <span className="trigger-label">{isOpen ? "Close Assistant" : "FLINT Assistant"}</span>
      </button>

      {/* Floating Drawer / Pop-up */}
      {isOpen && (
        <div className="floating-chat-window">
          {/* Header */}
          <div className="chat-window-header">
            <div className="chat-title-group">
              <span className="chat-avatar">🤖</span>
              <div>
                <h4>FLINT Assistant</h4>
                <span className="chat-online-indicator">● RAG Academic Engine Active</span>
              </div>
            </div>
            <button
              className="chat-minimize-btn"
              onClick={() => setIsOpen(false)}
            >
              ✕
            </button>
          </div>

          {/* Messages Body */}
          <div className="chat-window-body">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`chat-bubble-row ${m.sender === "student" ? "student" : "bot"}`}
              >
                <div className={`chat-bubble ${m.sender === "student" ? "student" : "bot"}`}>
                  <p style={{ margin: 0, whiteSpace: "pre-wrap" }}>{m.message}</p>

                  {/* Sources citation pill */}
                  {m.sources && m.sources.length > 0 && (
                    <div className="chat-sources-accordion">
                      <strong>📚 Verified Sources:</strong>
                      {m.sources.map((src, i) => (
                        <div key={i} className="source-mini-tag">
                          📄 {src.link ? <Link to={src.link}>{src.title}</Link> : src.title}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {sending && (
              <div className="chat-bubble-row bot">
                <div className="chat-bubble bot typing">
                  <span>Assistant is researching your question...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Quick Chips */}
          <div className="chat-chips-scroll">
            {suggestedChips.slice(0, 3).map((chip, idx) => (
              <button
                key={idx}
                className="chat-chip-btn"
                onClick={() => handleSendMessage(chip)}
              >
                {chip}
              </button>
            ))}
          </div>

          {/* Input Box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="chat-window-input-form"
          >
            <input
              type="text"
              placeholder="Ask about exams, courses, or syllabus..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              className="chat-input-field"
            />
            <button
              type="submit"
              className="chat-send-btn"
              disabled={sending || !inputMessage.trim()}
            >
              ➤
            </button>
          </form>
        </div>
      )}
    </>
  );
}

export default ChatWidget;
