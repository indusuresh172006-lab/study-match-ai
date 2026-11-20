import { useState, useEffect, useRef } from "react";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";
import EmptyState from "../components/EmptyState";

function AIMentor({ user }) {
  // Sessions State
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [loadingSessions, setLoadingSessions] = useState(true);

  // Messages State
  const [messages, setMessages] = useState([]);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [inputMessage, setInputMessage] = useState("");
  const [sending, setSending] = useState(false);

  // Student Context & Suggested Chips
  const [weakTopics, setWeakTopics] = useState([]);
  const [suggestedChips, setSuggestedChips] = useState([
    "What entrance exams should I focus on?",
    "Which courses best match my skill profile?",
    "How can I improve my weak topics?",
    "Explain the difference between JEE Main and JEE Advanced.",
  ]);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Fetch student weak topics
  const fetchWeakTopics = async () => {
    try {
      const res = await api.get("/skill-profile/summary");
      const weaks = (res.data?.topics || []).filter((t) => t.status === "weak");
      setWeakTopics(weaks);
    } catch (err) {
      console.error("Error fetching skills:", err);
    }
  };

  // Fetch all sessions
  const fetchSessions = async () => {
    setLoadingSessions(true);
    try {
      const res = await api.get("/api/v1/chat/sessions");
      setSessions(res.data || []);
      if (res.data && res.data.length > 0 && !activeSessionId) {
        setActiveSessionId(res.data[0].session_id);
        fetchMessages(res.data[0].session_id);
      }
    } catch (err) {
      console.error("Error fetching sessions:", err);
    } finally {
      setLoadingSessions(false);
    }
  };

  // Fetch messages for a session
  const fetchMessages = async (sId) => {
    setLoadingMessages(true);
    try {
      const res = await api.get(`/api/v1/chat/sessions/${sId}/messages`);
      if (res.data && res.data.length > 0) {
        setMessages(res.data);
      } else {
        setMessages([
          {
            id: 1,
            sender: "bot",
            message: `Hello ${user?.name || "Student"}! 👋 I am your FLINT Assistant, backed by official guidance documents and your personal skill profile. How can I help you excel today?`,
          },
        ]);
      }
    } catch (err) {
      console.error("Error fetching messages:", err);
    } finally {
      setLoadingMessages(false);
    }
  };

  useEffect(() => {
    fetchSessions();
    fetchWeakTopics();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, sending]);

  // Create new session
  const handleCreateSession = async () => {
    try {
      const res = await api.post("/api/v1/chat/sessions", {
        title: "New Study Discussion",
      });
      const newSess = {
        session_id: res.data.session_id,
        title: res.data.title,
        created_at: res.data.created_at,
        message_count: 0,
      };
      setSessions([newSess, ...sessions]);
      setActiveSessionId(newSess.session_id);
      setMessages([
        {
          id: 1,
          sender: "bot",
          message: `Started a fresh discussion thread. Ask me about exams, courses, study strategies, or syllabus concepts!`,
        },
      ]);
    } catch (err) {
      console.error("Failed to create session:", err);
      alert("Unable to create a new session.");
    }
  };

  // Delete session
  const handleDeleteSession = async (sId, e) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this discussion thread?")) return;
    try {
      await api.delete(`/api/v1/chat/sessions/${sId}`);
      const remaining = sessions.filter((s) => s.session_id !== sId);
      setSessions(remaining);
      if (activeSessionId === sId) {
        if (remaining.length > 0) {
          setActiveSessionId(remaining[0].session_id);
          fetchMessages(remaining[0].session_id);
        } else {
          setActiveSessionId(null);
          setMessages([]);
        }
      }
    } catch (err) {
      console.error("Delete session error:", err);
    }
  };

  // Send message
  const handleSendMessage = async (customText) => {
    const textToSend = customText || inputMessage;
    if (!textToSend.trim() || sending) return;

    let targetSessionId = activeSessionId;
    if (!targetSessionId) {
      try {
        const newSess = await api.post("/api/v1/chat/sessions", {
          title: textToSend.substring(0, 30),
        });
        targetSessionId = newSess.data.session_id;
        setActiveSessionId(targetSessionId);
        setSessions([newSess.data, ...sessions]);
      } catch (err) {
        alert("Could not start discussion.");
        return;
      }
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
      const res = await api.post(`/api/v1/chat/sessions/${targetSessionId}/message`, {
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
      // Refresh session titles
      api.get("/api/v1/chat/sessions").then((r) => setSessions(r.data || []));
    } catch (err) {
      console.error("Send message error:", err);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 2,
          sender: "bot",
          message: "I am having trouble reaching the mentoring service right now. Please try again shortly.",
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="ai-mentor-page">
      {/* Page Header */}
      <div className="page-header-row">
        <div>
          <h2>🤖 FLINT Assistant & Personal AI Mentor</h2>
          <p className="page-subtitle">
            RAG-powered conversational mentor referencing verified exam syllabi, college directories, and your personal topic mastery profile.
          </p>
        </div>
        <button className="action-btn-primary" onClick={handleCreateSession}>
          + New Discussion
        </button>
      </div>

      {/* Main Two-Column Chat Container */}
      <div className="mentor-layout-split">
        {/* Left Sidebar: Threads & Weak Topics Context */}
        <div className="mentor-threads-sidebar">
          <div className="sidebar-list-header">
            <h4>💬 Discussion Threads</h4>
            <span className="results-count">{sessions.length} Threads</span>
          </div>

          <div className="threads-list">
            {loadingSessions ? (
              <p style={{ padding: "12px", fontSize: "13px", color: "var(--text-muted)" }}>
                Loading discussions...
              </p>
            ) : sessions.length === 0 ? (
              <p style={{ padding: "12px", fontSize: "13px", color: "var(--text-muted)" }}>
                No active discussions. Click + New Discussion to start!
              </p>
            ) : (
              sessions.map((s) => (
                <div
                  key={s.session_id}
                  className={`thread-item-row ${s.session_id === activeSessionId ? "active" : ""}`}
                  onClick={() => {
                    setActiveSessionId(s.session_id);
                    fetchMessages(s.session_id);
                  }}
                >
                  <div className="thread-info">
                    <span className="thread-title">{s.title || "Study Discussion"}</span>
                    <span className="thread-date">
                      {new Date(s.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <button
                    className="thread-delete-btn"
                    title="Delete thread"
                    onClick={(e) => handleDeleteSession(s.session_id, e)}
                  >
                    🗑️
                  </button>
                </div>
              ))
            )}
          </div>

          {/* Student Weak Topics Context Banner */}
          <div className="mentor-weak-context-box">
            <h4>🎯 Active Skill Context:</h4>
            <p style={{ fontSize: "11px", color: "var(--text-muted)", margin: "4px 0 8px" }}>
              Injected into prompts so guidance automatically targets your growth areas.
            </p>
            <div className="pills-wrap">
              {weakTopics.length > 0 ? (
                weakTopics.map((w, i) => (
                  <span key={i} className="danger-topic-pill">
                    ⚠️ {w.topic} ({w.mastery_score}%)
                  </span>
                ))
              ) : (
                <span className="match-badge match-high">✓ Strong Profile</span>
              )}
            </div>
          </div>
        </div>

        {/* Right Chat Column */}
        <div className="mentor-chat-column">
          {/* Chat Header Bar */}
          <div className="mentor-chat-top-bar">
            <div className="mentor-profile-group">
              <span className="mentor-avatar-badge">🤖</span>
              <div>
                <strong>FLINT Assistant</strong>
                <span className="online-tag">● Powered by Gemini 1.5 & Verified RAG Database</span>
              </div>
            </div>
          </div>

          {/* Message Stream */}
          <div className="mentor-messages-scroll-area">
            {loadingMessages ? (
              <LoadingSpinner message="Retrieving conversation history..." />
            ) : (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`chat-message-bubble-row ${
                    msg.sender === "student" ? "student" : "bot"
                  }`}
                >
                  <div
                    className={`mentor-chat-bubble ${
                      msg.sender === "student" ? "student" : "bot"
                    }`}
                  >
                    <p style={{ margin: 0, whiteSpace: "pre-wrap" }}>{msg.message}</p>

                    {/* Sources Citations Pill */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="rag-sources-box">
                        <strong>📚 Verified Guidance Sources:</strong>
                        <div style={{ display: "flex", flexDirection: "column", gap: "4px", marginTop: "4px" }}>
                          {msg.sources.map((src, idx) => (
                            <div key={idx} className="rag-source-item">
                              📄 <strong>{src.title}</strong>
                              {src.snippet && (
                                <span className="source-snippet"> — "{src.snippet.substring(0, 120)}..."</span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}

            {sending && (
              <div className="chat-message-bubble-row bot">
                <div className="mentor-chat-bubble bot typing">
                  <span>Assistant is analyzing syllabus knowledge base and your skill profile...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Quick Question Chips */}
          <div className="suggested-chips-container">
            <span className="chips-label">💡 Suggested Questions:</span>
            <div className="chips-scroll">
              {suggestedChips.map((chip, idx) => (
                <button
                  key={idx}
                  className="quick-chip-btn"
                  onClick={() => handleSendMessage(chip)}
                  disabled={sending}
                >
                  {chip}
                </button>
              ))}
            </div>
          </div>

          {/* Message Input Box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="mentor-input-form"
          >
            <input
              type="text"
              placeholder="Ask about exam eligibility, syllabus breakdown, career roadmaps, or study tips..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              className="mentor-text-input"
            />
            <button
              type="submit"
              className="action-btn-primary"
              disabled={sending || !inputMessage.trim()}
            >
              {sending ? "Thinking..." : "Send Message 🚀"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default AIMentor;
