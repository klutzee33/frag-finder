import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Components
const Sidebar = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: 'templates', name: 'Templates', icon: '📋' },
    { id: 'inventory', name: 'Inventory', icon: '🖥️' },
    { id: 'execute', name: 'Execute', icon: '⚡' },
    { id: 'logs', name: 'Execution Logs', icon: '📊' },
    { id: 'ssh', name: 'SSH Keys', icon: '🔐' }
  ];

  return (
    <div className="bg-gray-900 w-64 min-h-screen p-4 border-r border-gray-700">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-2">Ansible Manager</h1>
        <p className="text-gray-400 text-sm">RHEL 8 Script Writer & Executor</p>
      </div>
      
      <nav className="space-y-2">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
              activeTab === tab.id 
                ? 'bg-blue-600 text-white' 
                : 'text-gray-300 hover:bg-gray-800 hover:text-white'
            }`}
          >
            <span className="text-lg">{tab.icon}</span>
            <span>{tab.name}</span>
          </button>
        ))}
      </nav>
    </div>
  );
};

const TemplateCard = ({ template, onSelect, onEdit }) => (
  <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 hover:border-blue-500 transition-colors">
    <div className="flex justify-between items-start mb-3">
      <h3 className="text-lg font-semibold text-white">{template.name}</h3>
      <span className="bg-blue-600 text-white text-xs px-2 py-1 rounded">{template.category}</span>
    </div>
    <p className="text-gray-400 text-sm mb-4">{template.description}</p>
    
    <div className="flex space-x-2">
      <button
        onClick={() => onSelect(template)}
        className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded text-sm transition-colors"
      >
        Use Template
      </button>
      <button
        onClick={() => onEdit(template)}
        className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded text-sm transition-colors"
      >
        Edit
      </button>
    </div>
  </div>
);

const TemplatesTab = ({ templates, onSelectTemplate, setActiveTab }) => {
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [showEditor, setShowEditor] = useState(false);
  const [customTemplate, setCustomTemplate] = useState({
    id: '',
    name: '',
    description: '',
    category: 'Custom',
    playbook_content: '---\n- name: Custom Playbook\n  hosts: all\n  become: yes\n  tasks:\n    - name: Example task\n      debug:\n        msg: "Hello from custom template"'
  });

  const handleCreateCustom = async () => {
    try {
      const templateData = {
        ...customTemplate,
        id: customTemplate.name.toLowerCase().replace(/\s+/g, '_'),
        variables: {}
      };
      
      await axios.post(`${API_BASE}/templates`, templateData);
      setShowEditor(false);
      setCustomTemplate({
        id: '',
        name: '',
        description: '',
        category: 'Custom',
        playbook_content: '---\n- name: Custom Playbook\n  hosts: all\n  become: yes\n  tasks:\n    - name: Example task\n      debug:\n        msg: "Hello from custom template"'
      });
      // Refresh templates
      window.location.reload();
    } catch (error) {
      console.error('Error creating template:', error);
    }
  };

  if (showEditor) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-white">Create Custom Template</h2>
          <button
            onClick={() => setShowEditor(false)}
            className="text-gray-400 hover:text-white"
          >
            ✕
          </button>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Template Name</label>
              <input
                type="text"
                value={customTemplate.name}
                onChange={(e) => setCustomTemplate({...customTemplate, name: e.target.value})}
                className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                placeholder="My Custom Template"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
              <textarea
                value={customTemplate.description}
                onChange={(e) => setCustomTemplate({...customTemplate, description: e.target.value})}
                className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                rows="3"
                placeholder="Describe what this template does..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Category</label>
              <input
                type="text"
                value={customTemplate.category}
                onChange={(e) => setCustomTemplate({...customTemplate, category: e.target.value})}
                className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                placeholder="Custom"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Playbook Content (YAML)</label>
            <textarea
              value={customTemplate.playbook_content}
              onChange={(e) => setCustomTemplate({...customTemplate, playbook_content: e.target.value})}
              className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none font-mono text-sm"
              rows="20"
              placeholder="Enter your Ansible playbook YAML here..."
            />
          </div>
        </div>
        
        <div className="flex space-x-4">
          <button
            onClick={handleCreateCustom}
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg transition-colors"
          >
            Create Template
          </button>
          <button
            onClick={() => setShowEditor(false)}
            className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-lg transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">Ansible Templates</h2>
        <button
          onClick={() => setShowEditor(true)}
          className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          + Create Custom
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map(template => (
          <TemplateCard
            key={template.id}
            template={template}
            onSelect={() => {
              onSelectTemplate(template);
              setActiveTab('execute');
            }}
            onEdit={() => {
              setSelectedTemplate(template);
              setShowEditor(true);
            }}
          />
        ))}
      </div>
    </div>
  );
};

const InventoryTab = ({ inventory, setInventory }) => {
  const [hosts, setHosts] = useState(inventory);
  const [newHost, setNewHost] = useState({
    name: '',
    ip: '',
    user: 'root',
    equipment_type: 'server',
    location: 'datacenter'
  });
  const [showAddForm, setShowAddForm] = useState(false);

  const handleAddHost = () => {
    if (newHost.name && newHost.ip) {
      const updatedHosts = [...hosts, newHost];
      setHosts(updatedHosts);
      setNewHost({
        name: '',
        ip: '',
        user: 'root',
        equipment_type: 'server',
        location: 'datacenter'
      });
      setShowAddForm(false);
    }
  };

  const handleSaveInventory = async () => {
    try {
      await axios.post(`${API_BASE}/inventory`, hosts);
      setInventory(hosts);
      alert('Inventory saved successfully!');
    } catch (error) {
      console.error('Error saving inventory:', error);
      alert('Failed to save inventory');
    }
  };

  const handleRemoveHost = (index) => {
    const updatedHosts = hosts.filter((_, i) => i !== index);
    setHosts(updatedHosts);
  };

  // Group hosts by equipment type and location
  const groupedHosts = hosts.reduce((acc, host) => {
    const key = `${host.equipment_type}-${host.location}`;
    if (!acc[key]) {
      acc[key] = { equipment_type: host.equipment_type, location: host.location, hosts: [] };
    }
    acc[key].hosts.push(host);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">Inventory Management</h2>
        <div className="space-x-3">
          <button
            onClick={() => setShowAddForm(true)}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            + Add Host
          </button>
          <button
            onClick={handleSaveInventory}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Save Inventory
          </button>
        </div>
      </div>

      {showAddForm && (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Add New Host</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <input
              type="text"
              placeholder="Host Name"
              value={newHost.name}
              onChange={(e) => setNewHost({...newHost, name: e.target.value})}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
            />
            <input
              type="text"
              placeholder="IP Address"
              value={newHost.ip}
              onChange={(e) => setNewHost({...newHost, ip: e.target.value})}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
            />
            <input
              type="text"
              placeholder="SSH User"
              value={newHost.user}
              onChange={(e) => setNewHost({...newHost, user: e.target.value})}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
            />
            <select
              value={newHost.equipment_type}
              onChange={(e) => setNewHost({...newHost, equipment_type: e.target.value})}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
            >
              <option value="server">Server</option>
              <option value="workstation">Workstation</option>
              <option value="router">Router</option>
              <option value="switch">Switch</option>
              <option value="firewall">Firewall</option>
            </select>
            <input
              type="text"
              placeholder="Location"
              value={newHost.location}
              onChange={(e) => setNewHost({...newHost, location: e.target.value})}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div className="flex space-x-3 mt-4">
            <button
              onClick={handleAddHost}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded transition-colors"
            >
              Add Host
            </button>
            <button
              onClick={() => setShowAddForm(false)}
              className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="space-y-6">
        {Object.entries(groupedHosts).map(([key, group]) => (
          <div key={key} className="bg-gray-800 border border-gray-700 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-4">
              {group.equipment_type.charAt(0).toUpperCase() + group.equipment_type.slice(1)}s - {group.location}
              <span className="text-sm text-gray-400 ml-2">({group.hosts.length} hosts)</span>
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-gray-400 border-b border-gray-600">
                    <th className="text-left py-2">Name</th>
                    <th className="text-left py-2">IP Address</th>
                    <th className="text-left py-2">User</th>
                    <th className="text-left py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {group.hosts.map((host, index) => (
                    <tr key={`${host.name}-${index}`} className="text-white border-b border-gray-700">
                      <td className="py-2">{host.name}</td>
                      <td className="py-2">{host.ip}</td>
                      <td className="py-2">{host.user}</td>
                      <td className="py-2">
                        <button
                          onClick={() => handleRemoveHost(hosts.indexOf(host))}
                          className="text-red-400 hover:text-red-300 text-sm"
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const ExecuteTab = ({ templates, inventory, selectedTemplate }) => {
  const [currentTemplate, setCurrentTemplate] = useState(selectedTemplate);
  const [selectedHosts, setSelectedHosts] = useState([]);
  const [variables, setVariables] = useState({});
  const [dryRun, setDryRun] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [output, setOutput] = useState('');
  const [customPlaybook, setCustomPlaybook] = useState('');
  const [useCustom, setUseCustom] = useState(false);

  useEffect(() => {
    if (selectedTemplate) {
      setCurrentTemplate(selectedTemplate);
      setVariables(selectedTemplate.variables || {});
    }
  }, [selectedTemplate]);

  const handleExecute = async () => {
    if (selectedHosts.length === 0) {
      alert('Please select at least one host');
      return;
    }

    setExecuting(true);
    setOutput('');

    try {
      const requestData = {
        hosts: selectedHosts,
        variables: variables,
        dry_run: dryRun
      };

      if (useCustom) {
        requestData.custom_playbook = customPlaybook;
      } else if (currentTemplate) {
        requestData.template_id = currentTemplate.id;
      } else {
        alert('Please select a template or provide custom playbook');
        setExecuting(false);
        return;
      }

      const response = await fetch(`${API_BASE}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));
              if (data.line) {
                setOutput(prev => prev + data.line);
              } else if (data.status) {
                setOutput(prev => prev + `\n\n=== Execution ${data.status.toUpperCase()} ===\n`);
              } else if (data.error) {
                setOutput(prev => prev + `\n\nERROR: ${data.error}\n`);
              }
            } catch (e) {
              // Ignore malformed JSON
            }
          }
        }
      }
    } catch (error) {
      setOutput(prev => prev + `\n\nFailed to execute: ${error.message}\n`);
    } finally {
      setExecuting(false);
    }
  };

  const handleVariableChange = (key, value) => {
    setVariables(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">Execute Playbooks</h2>
        <div className="flex items-center space-x-4">
          <label className="flex items-center text-white">
            <input
              type="checkbox"
              checked={dryRun}
              onChange={(e) => setDryRun(e.target.checked)}
              className="mr-2"
            />
            Dry Run (Check Mode)
          </label>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configuration Panel */}
        <div className="space-y-6">
          {/* Template/Custom Selection */}
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-4">Playbook Source</h3>
            <div className="space-y-4">
              <label className="flex items-center text-white">
                <input
                  type="radio"
                  checked={!useCustom}
                  onChange={() => setUseCustom(false)}
                  className="mr-2"
                />
                Use Template
              </label>
              <label className="flex items-center text-white">
                <input
                  type="radio"
                  checked={useCustom}
                  onChange={() => setUseCustom(true)}
                  className="mr-2"
                />
                Custom Playbook
              </label>
            </div>

            {!useCustom && (
              <div className="mt-4">
                <select
                  value={currentTemplate?.id || ''}
                  onChange={(e) => {
                    const template = templates.find(t => t.id === e.target.value);
                    setCurrentTemplate(template);
                    setVariables(template?.variables || {});
                  }}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                >
                  <option value="">Select a template...</option>
                  {templates.map(template => (
                    <option key={template.id} value={template.id}>
                      {template.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {useCustom && (
              <div className="mt-4">
                <textarea
                  value={customPlaybook}
                  onChange={(e) => setCustomPlaybook(e.target.value)}
                  placeholder="Enter your custom Ansible playbook YAML here..."
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none font-mono text-sm"
                  rows="15"
                />
              </div>
            )}
          </div>

          {/* Host Selection */}
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-4">Target Hosts</h3>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {inventory.map((host, index) => (
                <label key={index} className="flex items-center text-white">
                  <input
                    type="checkbox"
                    checked={selectedHosts.includes(host.name)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedHosts(prev => [...prev, host.name]);
                      } else {
                        setSelectedHosts(prev => prev.filter(h => h !== host.name));
                      }
                    }}
                    className="mr-2"
                  />
                  <span className="text-sm">
                    {host.name} ({host.ip}) - {host.equipment_type}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Variables */}
          {!useCustom && currentTemplate && Object.keys(currentTemplate.variables || {}).length > 0 && (
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-4">Variables</h3>
              <div className="space-y-3">
                {Object.entries(currentTemplate.variables || {}).map(([key, defaultValue]) => (
                  <div key={key}>
                    <label className="block text-sm text-gray-300 mb-1">{key}</label>
                    <input
                      type="text"
                      value={variables[key] || defaultValue}
                      onChange={(e) => handleVariableChange(key, e.target.value)}
                      className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:border-blue-500 focus:outline-none text-sm"
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Execute Button */}
          <button
            onClick={handleExecute}
            disabled={executing}
            className={`w-full py-3 px-4 rounded-lg font-semibold transition-colors ${
              executing
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 text-white'
            }`}
          >
            {executing ? 'Executing...' : (dryRun ? 'Run Check' : 'Execute Playbook')}
          </button>
        </div>

        {/* Output Panel */}
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-white mb-4">Execution Output</h3>
          <div className="bg-black rounded-lg p-4 h-96 overflow-y-auto">
            <pre className="text-green-400 text-sm font-mono whitespace-pre-wrap">
              {output || 'No output yet. Click "Execute Playbook" to begin.'}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};

const SSHKeysTab = () => {
  const [keys, setKeys] = useState([]);
  const [generating, setGenerating] = useState(false);

  const loadKeys = async () => {
    try {
      const response = await axios.get(`${API_BASE}/ssh/keys`);
      setKeys(response.data);
    } catch (error) {
      console.error('Error loading SSH keys:', error);
    }
  };

  const generateKey = async () => {
    setGenerating(true);
    try {
      const keyName = `ansible_key_${Date.now()}`;
      await axios.post(`${API_BASE}/ssh/generate-key?key_name=${keyName}`);
      loadKeys();
    } catch (error) {
      console.error('Error generating SSH key:', error);
      alert('Failed to generate SSH key');
    } finally {
      setGenerating(false);
    }
  };

  useEffect(() => {
    loadKeys();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">SSH Key Management</h2>
        <button
          onClick={generateKey}
          disabled={generating}
          className={`px-4 py-2 rounded-lg transition-colors ${
            generating
              ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
              : 'bg-green-600 hover:bg-green-700 text-white'
          }`}
        >
          {generating ? 'Generating...' : '+ Generate New Key'}
        </button>
      </div>

      {keys.length === 0 ? (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-8 text-center">
          <div className="text-gray-400 mb-4">
            <span className="text-4xl">🔐</span>
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">No SSH Keys Found</h3>
          <p className="text-gray-400 mb-4">Generate a new SSH key pair to get started with remote host management.</p>
          <button
            onClick={generateKey}
            disabled={generating}
            className={`px-6 py-3 rounded-lg transition-colors ${
              generating
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 text-white'
            }`}
          >
            {generating ? 'Generating Key...' : 'Generate SSH Key'}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {keys.map((key, index) => (
            <div key={index} className="bg-gray-800 border border-gray-700 rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-semibold text-white">{key.name}</h3>
                  <p className="text-gray-400 text-sm">Private Key: {key.private_key_path}</p>
                  <p className="text-gray-400 text-sm">Public Key: {key.public_key_path}</p>
                </div>
              </div>
              <div className="mt-4">
                <label className="block text-sm text-gray-300 mb-2">Public Key Content:</label>
                <textarea
                  value={key.public_key_content}
                  readOnly
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm font-mono"
                  rows="3"
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const ExecutionLogsTab = () => {
  const [executions, setExecutions] = useState([]);
  const [selectedLog, setSelectedLog] = useState(null);

  const loadExecutions = async () => {
    try {
      const response = await axios.get(`${API_BASE}/executions`);
      setExecutions(response.data);
    } catch (error) {
      console.error('Error loading executions:', error);
    }
  };

  const loadExecutionLog = async (executionId) => {
    try {
      const response = await axios.get(`${API_BASE}/executions/${executionId}/log`);
      setSelectedLog(response.data);
    } catch (error) {
      console.error('Error loading execution log:', error);
    }
  };

  useEffect(() => {
    loadExecutions();
  }, []);

  if (selectedLog) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-white">Execution Log</h2>
          <button
            onClick={() => setSelectedLog(null)}
            className="text-gray-400 hover:text-white"
          >
            ← Back to Logs
          </button>
        </div>
        
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-white mb-4">Execution ID: {selectedLog.execution_id}</h3>
          <div className="bg-black rounded-lg p-4 h-96 overflow-y-auto">
            <pre className="text-green-400 text-sm font-mono whitespace-pre-wrap">
              {selectedLog.log_content}
            </pre>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">Execution History</h2>
        <button
          onClick={loadExecutions}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          Refresh
        </button>
      </div>

      {executions.length === 0 ? (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-8 text-center">
          <div className="text-gray-400 mb-4">
            <span className="text-4xl">📊</span>
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">No Executions Yet</h3>
          <p className="text-gray-400">Execute your first playbook to see logs here.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {executions.map((execution, index) => (
            <div
              key={index}
              className="bg-gray-800 border border-gray-700 rounded-lg p-4 hover:border-blue-500 transition-colors cursor-pointer"
              onClick={() => loadExecutionLog(execution.execution_id)}
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-semibold text-white">Execution {execution.execution_id.slice(0, 8)}...</h3>
                  <p className="text-gray-400 text-sm">
                    {new Date(execution.created_at).toLocaleString()}
                  </p>
                </div>
                <span className="text-blue-400 text-sm">View Log →</span>
              </div>
              <div className="mt-3">
                <pre className="text-gray-300 text-sm bg-gray-900 rounded p-2 overflow-hidden">
                  {execution.preview}
                </pre>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Main App Component
function App() {
  const [activeTab, setActiveTab] = useState('templates');
  const [templates, setTemplates] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [ansibleVersion, setAnsibleVersion] = useState(null);

  useEffect(() => {
    // Load initial data
    loadTemplates();
    loadInventory();
    checkAnsible();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await axios.get(`${API_BASE}/templates`);
      setTemplates(response.data);
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

  const loadInventory = async () => {
    try {
      const response = await axios.get(`${API_BASE}/inventory`);
      setInventory(response.data);
    } catch (error) {
      console.error('Error loading inventory:', error);
    }
  };

  const checkAnsible = async () => {
    try {
      const response = await axios.get(`${API_BASE}/ansible/version`);
      setAnsibleVersion(response.data);
    } catch (error) {
      console.error('Error checking Ansible:', error);
    }
  };

  const handleSelectTemplate = (template) => {
    setSelectedTemplate(template);
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'templates':
        return (
          <TemplatesTab
            templates={templates}
            onSelectTemplate={handleSelectTemplate}
            setActiveTab={setActiveTab}
          />
        );
      case 'inventory':
        return (
          <InventoryTab
            inventory={inventory}
            setInventory={setInventory}
          />
        );
      case 'execute':
        return (
          <ExecuteTab
            templates={templates}
            inventory={inventory}
            selectedTemplate={selectedTemplate}
          />
        );
      case 'ssh':
        return <SSHKeysTab />;
      case 'logs':
        return <ExecutionLogsTab />;
      default:
        return <TemplatesTab templates={templates} onSelectTemplate={handleSelectTemplate} setActiveTab={setActiveTab} />;
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-900">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <div className="flex-1 p-6">
        {/* Header */}
        <div className="mb-6 pb-4 border-b border-gray-700">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-white">Ansible Script Writer & Executor</h1>
              <p className="text-gray-400 mt-1">RHEL 8 Automation Platform</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-400">
                Ansible Status: {' '}
                <span className={ansibleVersion?.installed ? 'text-green-400' : 'text-red-400'}>
                  {ansibleVersion?.installed ? '✓ Installed' : '✗ Not Found'}
                </span>
              </div>
              {ansibleVersion?.version && (
                <div className="text-xs text-gray-500">{ansibleVersion.version}</div>
              )}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}

export default App;