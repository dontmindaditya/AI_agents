"""
Seed Agents Script
Run this script to populate the database with example AI agents.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load env variables from root or backend
root_dir = os.path.join(os.path.dirname(__file__), "..", "..")
backend_dir = os.path.join(os.path.dirname(__file__), "..")

if os.path.exists(os.path.join(root_dir, ".env")):
    load_dotenv(os.path.join(root_dir, ".env"))
elif os.path.exists(os.path.join(backend_dir, ".env")):
    load_dotenv(os.path.join(backend_dir, ".env"))
else:
    print("Warning: .env file not found")

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database.client import supabase_client

HELP_BOT_FRONTEND = """
'use client';
import { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send } from 'lucide-react';

export default function HelpBot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<{role: 'user'|'assistant', content: string}[]>([
    {role: 'assistant', content: 'Hi! How can I help you today?'}
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, {role: 'user', content: userMsg}]);
    setLoading(true);

    try {
      const res = await fetch('/api/agents/help-bot/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ message: userMsg })
      });
      
      const data = await res.json();
      setMessages(prev => [...prev, {role: 'assistant', content: data.reply}]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, {role: 'assistant', content: 'Sorry, I encountered an error.'}]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 font-sans">
      {!isOpen && (
        <button 
          onClick={() => setIsOpen(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-lg transition-transform hover:scale-110"
        >
          <MessageCircle size={24} />
        </button>
      )}

      {isOpen && (
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-2xl w-80 sm:w-96 flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-10 duration-200">
          <div className="bg-blue-600 p-4 flex justify-between items-center text-white">
            <h3 className="font-semibold">Support Assistant</h3>
            <button onClick={() => setIsOpen(false)} className="hover:bg-blue-700 p-1 rounded">
              <X size={18} />
            </button>
          </div>
          
          <div className="h-96 overflow-y-auto p-4 space-y-4 bg-zinc-50 dark:bg-zinc-950/50">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] p-3 rounded-2xl text-sm ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white rounded-br-none' 
                    : 'bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-bl-none'
                }`}>
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white dark:bg-zinc-800 p-3 rounded-2xl rounded-bl-none border border-zinc-200 dark:border-zinc-700 text-sm animate-pulse">
                  Typing...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="p-3 bg-white dark:bg-zinc-900 border-t border-zinc-200 dark:border-zinc-800 flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type a message..."
              className="flex-1 bg-zinc-100 dark:bg-zinc-800 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button 
              type="submit" 
              disabled={loading || !input.trim()}
              className="bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 disabled:opacity-50"
            >
              <Send size={18} />
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
"""

HELP_BOT_BACKEND = """
import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const { message } = await req.json();
    
    // In a real agent, this would call OpenAI/Anthropic
    // For demo purposes, we return a simulated AI response
    
    await new Promise(r => setTimeout(r, 1000)); // Simulate latency
    
    let reply = "I'm a demo agent! I received your message: " + message;
    
    if (message.toLowerCase().includes('help')) {
        reply = "I can help you navigate this website or answer questions about our services.";
    } else if (message.toLowerCase().includes('price')) {
        reply = "Our pricing plans start at $29/mo for the Pro tier.";
    }
    
    return NextResponse.json({ reply });
  } catch (error) {
    return NextResponse.json({ error: 'Internal Error' }, { status: 500 });
  }
}
"""

LEAD_CAPTURE_FRONTEND = """
'use client';
import { useState, useEffect } from 'react';
import { Mail, X, Check } from 'lucide-react';

export default function LeadCapture() {
  const [isVisible, setIsVisible] = useState(false);
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    // Show after 5 seconds if not dismissed
    const timer = setTimeout(() => {
      if (!dismissed) setIsVisible(true);
    }, 5000);
    return () => clearTimeout(timer);
  }, [dismissed]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await fetch('/api/agents/lead-capture/capture', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ email })
      });
      setSubmitted(true);
      setTimeout(() => {
        setIsVisible(false);
        setDismissed(true);
      }, 3000);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="bg-white dark:bg-zinc-900 rounded-2xl shadow-2xl max-w-sm w-full p-6 relative animate-in zoom-in-95 duration-300">
        <button 
          onClick={() => {setIsVisible(false); setDismissed(true);}}
          className="absolute top-4 right-4 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200"
        >
          <X size={20} />
        </button>

        <div className="text-center space-y-4">
          <div className="mx-auto w-12 h-12 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-full flex items-center justify-center">
            {submitted ? <Check size={24} /> : <Mail size={24} />}
          </div>
          
          <h3 className="text-xl font-bold">
            {submitted ? "You're on the list!" : "Get Early Access"}
          </h3>
          
          <p className="text-sm text-zinc-500 dark:text-zinc-400">
            {submitted 
              ? "Thanks for subscribing. We'll be in touch soon." 
              : "Join 2,000+ others and never miss a product update."}
          </p>

          {!submitted && (
            <form onSubmit={handleSubmit} className="space-y-3">
              <input
                type="email"
                required
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 focus:ring-2 focus:ring-purple-500 outline-none transition-all"
              />
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 rounded-lg transition-colors disabled:opacity-50"
              >
                {loading ? 'Subscribing...' : 'Subscribe Now'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
"""

LEAD_CAPTURE_BACKEND = """
import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  // In a real app, save to database
  console.log("Lead Captured!");
  return NextResponse.json({ success: true });
}
"""

agents = [
    {
        "name": "24/7 Help Bot",
        "slug": "help-bot",
        "description": "AI customer support chatbot that answers questions instantly.",
        "detailed_description": "A fully functional AI chatbot that floats in the bottom right corner. Connects to OpenAI or Anthropic to answer user queries about your website.",
        "category_slug": "support",
        "pricing_tier": "free",
        "frontend_component_code": HELP_BOT_FRONTEND,
        "backend_api_code": HELP_BOT_BACKEND,
        "config_schema": {
            "type": "object",
            "required": ["welcome_message"],
            "properties": {
                "welcome_message": {
                    "type": "string",
                    "title": "Welcome Message",
                    "default": "Hi! How can I help you today?",
                    "description": "First message user sees"
                },
                "theme_color": {
                    "type": "string",
                    "title": "Theme Color",
                    "default": "#2563eb",
                    "description": "Main color for the chat button"
                }
            }
        },
        "dependencies": {"lucide-react": "latest"},
        "is_active": True,
        "metadata": {"rating": 4.8, "install_count": 1240}
    },
    {
        "name": "Smart Lead Capture",
        "slug": "lead-capture",
        "description": "Popup modal to collect emails from visitors.",
        "detailed_description": "Beautiful entry popup that appears after 5 seconds to capture visitor emails. Includes success state and dismissal logic.",
        "category_slug": "marketing",
        "pricing_tier": "pro",
        "frontend_component_code": LEAD_CAPTURE_FRONTEND,
        "backend_api_code": LEAD_CAPTURE_BACKEND,
        "config_schema": {
            "type": "object",
            "properties": {
                "delay_seconds": {
                    "type": "number", 
                    "title": "Delay (seconds)",
                    "default": 5
                },
                "heading_text": {
                    "type": "string",
                    "title": "Heading Text",
                    "default": "Get Early Access"
                }
            }
        },
        "dependencies": {"lucide-react": "latest"},
        "is_active": True,
        "metadata": {"rating": 4.7, "install_count": 850}
    }
]

async def seed():
    print("Seeding agents...")
    
    # 1. Fetch Categories
    cat_res = supabase_client.client.table("agent_categories").select("id, slug").execute()
    cat_map = {c['slug']: c['id'] for c in cat_res.data}
    
    for agent in agents:
        cat_slug = agent.pop("category_slug")
        if cat_slug not in cat_map:
            print(f"Category '{cat_slug}' not found, skipping {agent['name']}")
            continue
            
        agent["category_id"] = cat_map[cat_slug]
        
        # Check if exists
        res = supabase_client.client.table("agent_catalog").select("id").eq("slug", agent["slug"]).execute()
        
        if res.data:
            print(f"Updating {agent['name']}...")
            supabase_client.client.table("agent_catalog").update(agent).eq("slug", agent["slug"]).execute()
        else:
            print(f"Creating {agent['name']}...")
            supabase_client.client.table("agent_catalog").insert(agent).execute()
            
    print("Seed complete!")

if __name__ == "__main__":
    asyncio.run(seed())
