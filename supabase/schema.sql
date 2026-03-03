-- AI Agent Marketplace Schema

-- Enable UUID extension if not enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Projects Table (Basic definition to support relationships)
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY, -- Using TEXT to support various ID formats (UUID or string)
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Agent Categories Table
CREATE TABLE IF NOT EXISTS agent_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Agent Catalog Table
CREATE TABLE IF NOT EXISTS agent_catalog (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    detailed_description TEXT,
    icon_url TEXT,
    category_id UUID REFERENCES agent_categories(id),
    pricing_tier TEXT DEFAULT 'free' CHECK (pricing_tier IN ('free', 'pro', 'enterprise')),
    
    -- Technical Components
    frontend_component_code TEXT,       -- React component code
    backend_api_code TEXT,              -- Backend API implementation
    dependencies JSONB DEFAULT '{}',     -- NPM dependencies: {"name": "version"}
    env_vars JSONB DEFAULT '[]',        -- Required env vars: [{"name": "", "description": ""}]
    
    -- Configuration
    config_schema JSONB DEFAULT '{}',   -- JSON Schema for user configuration
    
    -- Metadata
    is_active BOOLEAN DEFAULT false,
    version TEXT DEFAULT '1.0.0',
    metadata JSONB DEFAULT '{}',        -- Ratings, install count, etc.
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Project Agents (Installed Agents)
CREATE TABLE IF NOT EXISTS project_agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id TEXT REFERENCES projects(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agent_catalog(id) ON DELETE CASCADE,
    
    config JSONB DEFAULT '{}',          -- User's configuration values
    is_enabled BOOLEAN DEFAULT true,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    
    UNIQUE(project_id, agent_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_catalog_slug ON agent_catalog(slug);
CREATE INDEX IF NOT EXISTS idx_agent_catalog_category ON agent_catalog(category_id);
CREATE INDEX IF NOT EXISTS idx_project_agents_project ON project_agents(project_id);

-- Seed Categories
INSERT INTO agent_categories (name, slug, description) VALUES
('Customer Support', 'support', 'Chatbots and help desk agents'),
('Marketing', 'marketing', 'Lead generation and email automation'),
('Productivity', 'productivity', 'Search and workflow tools'),
('Analytics', 'analytics', 'Tracking and insights'),
('Design', 'design', 'UI/UX enhancements'),
('Communication', 'communication', 'Translation and social tools'),
('Security', 'security', 'Authentication and protection'),
('SEO', 'seo', 'Search engine optimization')
ON CONFLICT (slug) DO NOTHING;
