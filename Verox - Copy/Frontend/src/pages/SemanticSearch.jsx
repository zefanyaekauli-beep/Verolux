import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Search, Filter, Clock, FileText, AlertTriangle, 
  Users, Car, Shield, TrendingUp, Zap,
  ChevronDown, X, Loader2, Sparkles
} from 'lucide-react'

const SemanticSearch = () => {
  const [query, setQuery] = useState('')
  const [searchType, setSearchType] = useState('all')
  const [results, setResults] = useState([])
  const [isSearching, setIsSearching] = useState(false)
  const [suggestions, setSuggestions] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [analytics, setAnalytics] = useState(null)
  const [recentSearches, setRecentSearches] = useState([])
  const searchInputRef = useRef(null)
  const suggestionsRef = useRef(null)

  // Search types configuration
  const searchTypes = [
    { id: 'all', label: 'All Sources', icon: Search, color: 'blue' },
    { id: 'detections', label: 'Detections', icon: Users, color: 'green' },
    { id: 'reports', label: 'Reports', icon: FileText, color: 'purple' },
    { id: 'violations', label: 'Violations', icon: AlertTriangle, color: 'red' }
  ]

  // Load analytics on component mount
  useEffect(() => {
    loadAnalytics()
    loadRecentSearches()
  }, [])

  // Handle input changes and get suggestions
  useEffect(() => {
    if (query.length >= 2) {
      getSuggestions(query)
    } else {
      setSuggestions([])
      setShowSuggestions(false)
    }
  }, [query])

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(event.target)) {
        setShowSuggestions(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const loadAnalytics = async () => {
    try {
      const response = await fetch('http://localhost:8003/search/analytics')
      if (response.ok) {
        const data = await response.json()
        setAnalytics(data)
      }
    } catch (error) {
      console.log('Analytics not available')
    }
  }

  const loadRecentSearches = () => {
    const recent = JSON.parse(localStorage.getItem('recentSearches') || '[]')
    setRecentSearches(recent)
  }

  const saveRecentSearch = (searchQuery) => {
    const recent = JSON.parse(localStorage.getItem('recentSearches') || '[]')
    const updated = [searchQuery, ...recent.filter(s => s !== searchQuery)].slice(0, 5)
    localStorage.setItem('recentSearches', JSON.stringify(updated))
    setRecentSearches(updated)
  }

  const getSuggestions = async (query) => {
    try {
      const response = await fetch(`http://localhost:8003/search/suggestions?q=${encodeURIComponent(query)}`)
      if (response.ok) {
        const data = await response.json()
        setSuggestions(data.suggestions)
        setShowSuggestions(true)
      }
    } catch (error) {
      console.log('Suggestions not available')
    }
  }

  const performSearch = async (searchQuery = query) => {
    if (!searchQuery.trim()) return

    setIsSearching(true)
    setShowSuggestions(false)
    
    try {
      const response = await fetch('http://localhost:8003/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          search_type: searchType,
          limit: 20
        })
      })

      if (response.ok) {
        const data = await response.json()
        setResults(data)
        saveRecentSearch(searchQuery)
      } else {
        console.error('Search failed')
        setResults([])
      }
    } catch (error) {
      console.error('Search error:', error)
      setResults([])
    } finally {
      setIsSearching(false)
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    performSearch()
  }

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion)
    performSearch(suggestion)
  }

  const handleRecentSearchClick = (recentQuery) => {
    setQuery(recentQuery)
    performSearch(recentQuery)
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'detection': return Users
      case 'report': return FileText
      case 'violation': return AlertTriangle
      default: return Search
    }
  }

  const getTypeColor = (type) => {
    switch (type) {
      case 'detection': return 'text-green-600 bg-green-50'
      case 'report': return 'text-purple-600 bg-purple-50'
      case 'violation': return 'text-red-600 bg-red-50'
      default: return 'text-blue-600 bg-blue-50'
    }
  }

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString()
  }

  const getRelevanceColor = (score) => {
    if (score >= 0.8) return 'text-green-600'
    if (score >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center mb-4">
            <Sparkles className="w-8 h-8 text-blue-600 mr-3" />
            <h1 className="text-3xl font-bold text-gray-900">Semantic Search</h1>
          </div>
          <p className="text-gray-600 text-lg">
            Search using natural language to find relevant information across all data sources
          </p>
        </motion.div>

        {/* Search Interface */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl shadow-lg p-6 mb-8"
        >
          <form onSubmit={handleSearch} className="space-y-6">
            {/* Search Input */}
            <div className="relative" ref={suggestionsRef}>
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  ref={searchInputRef}
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask anything in natural language... (e.g., 'person detected at main entrance', 'security incidents today')"
                  className="w-full pl-12 pr-4 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                />
                {isSearching && (
                  <Loader2 className="absolute right-4 top-1/2 transform -translate-y-1/2 w-5 h-5 animate-spin text-blue-600" />
                )}
              </div>

              {/* Suggestions Dropdown */}
              <AnimatePresence>
                {showSuggestions && suggestions.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-10"
                  >
                    {suggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="w-full px-4 py-3 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                      >
                        <div className="flex items-center">
                          <Search className="w-4 h-4 text-gray-400 mr-3" />
                          <span className="text-gray-700">{suggestion}</span>
                        </div>
                      </button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Search Type Filter */}
            <div className="flex flex-wrap gap-2">
              {searchTypes.map((type) => {
                const Icon = type.icon
                return (
                  <button
                    key={type.id}
                    onClick={() => setSearchType(type.id)}
                    className={`flex items-center px-4 py-2 rounded-lg border transition-colors ${
                      searchType === type.id
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {type.label}
                  </button>
                )
              })}
            </div>

            {/* Recent Searches */}
            {recentSearches.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Recent Searches</h3>
                <div className="flex flex-wrap gap-2">
                  {recentSearches.map((recent, index) => (
                    <button
                      key={index}
                      onClick={() => handleRecentSearchClick(recent)}
                      className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 transition-colors"
                    >
                      {recent}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </form>
        </motion.div>

        {/* Analytics Cards */}
        {analytics && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
          >
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center">
                <Users className="w-8 h-8 text-green-600 mr-3" />
                <div>
                  <p className="text-2xl font-bold text-gray-900">{analytics.total_detections}</p>
                  <p className="text-sm text-gray-600">Total Detections</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center">
                <FileText className="w-8 h-8 text-purple-600 mr-3" />
                <div>
                  <p className="text-2xl font-bold text-gray-900">{analytics.total_reports}</p>
                  <p className="text-sm text-gray-600">Reports</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center">
                <AlertTriangle className="w-8 h-8 text-red-600 mr-3" />
                <div>
                  <p className="text-2xl font-bold text-gray-900">{analytics.total_violations}</p>
                  <p className="text-sm text-gray-600">Violations</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center">
                <Zap className="w-8 h-8 text-blue-600 mr-3" />
                <div>
                  <p className="text-2xl font-bold text-gray-900">AI</p>
                  <p className="text-sm text-gray-600">Powered Search</p>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Search Results */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          {results.length > 0 ? (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Search Results ({results.length})
              </h2>
              {results.map((result, index) => {
                const TypeIcon = getTypeIcon(result.type)
                return (
                  <motion.div
                    key={result.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center">
                        <div className={`p-2 rounded-lg ${getTypeColor(result.type)} mr-3`}>
                          <TypeIcon className="w-5 h-5" />
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">{result.title}</h3>
                          <p className="text-sm text-gray-600">{formatTimestamp(result.timestamp)}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`text-sm font-medium ${getRelevanceColor(result.relevance_score)}`}>
                          {(result.relevance_score * 100).toFixed(1)}% match
                        </span>
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs">
                          {result.type}
                        </span>
                      </div>
                    </div>
                    <p className="text-gray-700 mb-4">{result.content}</p>
                    {Object.keys(result.metadata).length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(result.metadata).map(([key, value]) => (
                          <span
                            key={key}
                            className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs"
                          >
                            {key}: {String(value)}
                          </span>
                        ))}
                      </div>
                    )}
                  </motion.div>
                )
              })}
            </div>
          ) : query && !isSearching ? (
            <div className="text-center py-12">
              <Search className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
              <p className="text-gray-600">Try adjusting your search terms or search type</p>
            </div>
          ) : null}
        </motion.div>
      </div>
    </div>
  )
}

export default SemanticSearch

