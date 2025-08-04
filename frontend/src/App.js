import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Hero Section Component
const HeroSection = ({ onSearch }) => {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    onSearch({ query: searchQuery });
  };

  return (
    <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white py-20">
      <div className="max-w-6xl mx-auto px-4 text-center">
        <h1 className="text-5xl font-bold mb-6">
          Find Your Perfect Fragrance
        </h1>
        <p className="text-xl mb-8 text-purple-100">
          Compare prices from top discount retailers and save on designer fragrances
        </p>
        
        <form onSearch={searchQuery} className="max-w-2xl mx-auto flex gap-4">
          <div className="flex-1">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search fragrances, brands, or notes..."
              className="w-full px-6 py-4 rounded-lg text-gray-900 text-lg focus:outline-none focus:ring-4 focus:ring-purple-300"
            />
          </div>
          <button
            onClick={handleSearch}
            className="bg-white text-purple-600 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
          >
            Search
          </button>
        </form>
      </div>
    </div>
  );
};

// Filter Sidebar Component
const FilterSidebar = ({ filters, onFilterChange, brands, discounters }) => {
  const genders = ['Men', 'Women', 'Unisex'];
  const sortOptions = [
    { value: 'price_asc', label: 'Price: Low to High' },
    { value: 'price_desc', label: 'Price: High to Low' },
    { value: 'name_asc', label: 'Name: A to Z' },
    { value: 'brand_asc', label: 'Brand: A to Z' }
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 sticky top-6">
      <h3 className="text-lg font-semibold mb-4 text-gray-800">Filters</h3>
      
      {/* Brand Filter */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Brand</label>
        <select
          value={filters.brand || ''}
          onChange={(e) => onFilterChange({ ...filters, brand: e.target.value || null })}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="">All Brands</option>
          {brands.map(brand => (
            <option key={brand} value={brand}>{brand}</option>
          ))}
        </select>
      </div>

      {/* Gender Filter */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Gender</label>
        <select
          value={filters.gender || ''}
          onChange={(e) => onFilterChange({ ...filters, gender: e.target.value || null })}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="">All Genders</option>
          {genders.map(gender => (
            <option key={gender} value={gender}>{gender}</option>
          ))}
        </select>
      </div>

      {/* Price Range */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Price Range</label>
        <div className="flex gap-2">
          <input
            type="number"
            placeholder="Min"
            value={filters.min_price || ''}
            onChange={(e) => onFilterChange({ ...filters, min_price: e.target.value ? parseFloat(e.target.value) : null })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <input
            type="number"
            placeholder="Max"
            value={filters.max_price || ''}
            onChange={(e) => onFilterChange({ ...filters, max_price: e.target.value ? parseFloat(e.target.value) : null })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>
      </div>

      {/* Discounter Filter */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Discounter</label>
        <select
          value={filters.discounter || ''}
          onChange={(e) => onFilterChange({ ...filters, discounter: e.target.value || null })}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="">All Stores</option>
          {discounters.map(discounter => (
            <option key={discounter.id} value={discounter.id}>{discounter.name}</option>
          ))}
        </select>
      </div>

      {/* Sort By */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
        <select
          value={filters.sort_by || 'price_asc'}
          onChange={(e) => onFilterChange({ ...filters, sort_by: e.target.value })}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          {sortOptions.map(option => (
            <option key={option.value} value={option.value}>{option.label}</option>
          ))}
        </select>
      </div>

      {/* Clear Filters */}
      <button
        onClick={() => onFilterChange({ sort_by: 'price_asc' })}
        className="w-full bg-gray-200 text-gray-700 py-2 rounded-lg hover:bg-gray-300 transition-colors"
      >
        Clear Filters
      </button>
    </div>
  );
};

// Product Card Component
const ProductCard = ({ result, discounters, onViewDetails }) => {
  const { fragrance, prices, lowest_price, discounter_count } = result;
  
  const getDiscounterName = (discounterId) => {
    const discounter = discounters.find(d => d.id === discounterId);
    return discounter ? discounter.name : 'Unknown';
  };

  const lowestPriceInfo = prices.find(p => p.price === lowest_price);
  const savings = lowestPriceInfo?.original_price ? lowestPriceInfo.original_price - lowest_price : 0;

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
      <div className="aspect-w-1 aspect-h-1 bg-gray-200">
        <img
          src={fragrance.image_url || 'https://images.unsplash.com/photo-1541643600914-78b084683601?w=400'}
          alt={fragrance.name}
          className="w-full h-64 object-cover"
        />
      </div>
      
      <div className="p-6">
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-lg font-semibold text-gray-900">{fragrance.name}</h3>
          <span className="text-sm text-gray-500">{fragrance.size}</span>
        </div>
        
        <p className="text-purple-600 font-medium mb-2">{fragrance.brand}</p>
        <p className="text-sm text-gray-600 mb-3">{fragrance.type} • {fragrance.gender}</p>
        
        {fragrance.description && (
          <p className="text-sm text-gray-700 mb-4 line-clamp-2">{fragrance.description}</p>
        )}

        {/* Price Information */}
        <div className="border-t pt-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-2xl font-bold text-green-600">${lowest_price.toFixed(2)}</span>
            {savings > 0 && (
              <div className="text-right">
                <span className="text-sm text-gray-500 line-through">${lowestPriceInfo.original_price.toFixed(2)}</span>
                <span className="text-sm text-green-600 font-medium ml-2">Save ${savings.toFixed(2)}</span>
              </div>
            )}
          </div>
          
          <p className="text-xs text-gray-600 mb-3">
            Lowest price at {getDiscounterName(lowestPriceInfo?.discounter_id)}
          </p>
          
          <p className="text-xs text-purple-600 mb-4">
            Available at {discounter_count} store{discounter_count > 1 ? 's' : ''}
          </p>
          
          <div className="flex gap-2">
            <button
              onClick={() => onViewDetails(fragrance.id)}
              className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors text-sm"
            >
              Compare Prices
            </button>
            <button
              onClick={() => window.open(lowestPriceInfo?.product_url, '_blank')}
              className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors text-sm"
            >
              Buy Now
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Product Details Modal
const ProductModal = ({ fragrance, isOpen, onClose, discounters }) => {
  const [productDetails, setProductDetails] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && fragrance) {
      loadProductDetails();
    }
  }, [isOpen, fragrance]);

  const loadProductDetails = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/fragrances/${fragrance.id}`);
      setProductDetails(response.data);
    } catch (error) {
      console.error('Error loading product details:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-screen overflow-y-auto">
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-900">
            {fragrance?.name || 'Loading...'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading product details...</p>
          </div>
        ) : productDetails ? (
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Product Image and Info */}
              <div>
                <img
                  src={productDetails.fragrance.image_url || 'https://images.unsplash.com/photo-1541643600914-78b084683601?w=400'}
                  alt={productDetails.fragrance.name}
                  className="w-full rounded-lg mb-4"
                />
                <h3 className="text-xl font-semibold mb-2">{productDetails.fragrance.name}</h3>
                <p className="text-purple-600 font-medium mb-2">{productDetails.fragrance.brand}</p>
                <p className="text-gray-600 mb-4">
                  {productDetails.fragrance.type} • {productDetails.fragrance.gender} • {productDetails.fragrance.size}
                </p>
                {productDetails.fragrance.description && (
                  <p className="text-gray-700 mb-4">{productDetails.fragrance.description}</p>
                )}
                {productDetails.fragrance.notes && productDetails.fragrance.notes.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2">Notes:</h4>
                    <div className="flex flex-wrap gap-2">
                      {productDetails.fragrance.notes.map((note, index) => (
                        <span
                          key={index}
                          className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-sm"
                        >
                          {note}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Price Comparison */}
              <div>
                <h4 className="text-lg font-semibold mb-4">Price Comparison</h4>
                <div className="space-y-4">
                  {productDetails.price_comparison
                    .sort((a, b) => a.price_info.price - b.price_info.price)
                    .map((item, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h5 className="font-semibold">{item.discounter.name}</h5>
                          <p className="text-sm text-gray-600">{item.discounter.description}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-xl font-bold text-green-600">
                            ${item.price_info.price.toFixed(2)}
                          </p>
                          {item.price_info.original_price && (
                            <p className="text-sm text-gray-500 line-through">
                              ${item.price_info.original_price.toFixed(2)}
                            </p>
                          )}
                        </div>
                      </div>
                      {item.price_info.discount_percentage && (
                        <p className="text-sm text-green-600 font-medium mb-2">
                          {item.price_info.discount_percentage}% off
                        </p>
                      )}
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">
                          {item.price_info.availability}
                        </span>
                        <button
                          onClick={() => window.open(item.price_info.product_url, '_blank')}
                          className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 transition-colors text-sm"
                        >
                          Visit Store
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="p-8 text-center text-gray-600">
            Failed to load product details.
          </div>
        )}
      </div>
    </div>
  );
};

// Popular Fragrances Section
const PopularSection = ({ onViewDetails }) => {
  const [popularFragrances, setPopularFragrances] = useState([]);

  useEffect(() => {
    loadPopularFragrances();
  }, []);

  const loadPopularFragrances = async () => {
    try {
      const response = await axios.get(`${API_BASE}/popular`);
      setPopularFragrances(response.data.slice(0, 3)); // Show top 3
    } catch (error) {
      console.error('Error loading popular fragrances:', error);
    }
  };

  return (
    <div className="py-16 bg-gray-50">
      <div className="max-w-6xl mx-auto px-4">
        <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
          Popular Fragrances
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {popularFragrances.map((item, index) => (
            <div key={index} className="bg-white rounded-lg shadow-lg p-6 text-center">
              <img
                src={item.fragrance.image_url || 'https://images.unsplash.com/photo-1541643600914-78b084683601?w=400'}
                alt={item.fragrance.name}
                className="w-32 h-32 object-cover rounded-lg mx-auto mb-4"
              />
              <h3 className="text-lg font-semibold mb-2">{item.fragrance.name}</h3>
              <p className="text-purple-600 font-medium mb-2">{item.fragrance.brand}</p>
              <p className="text-2xl font-bold text-green-600 mb-2">
                From ${item.lowest_price.toFixed(2)}
              </p>
              <p className="text-sm text-gray-600 mb-4">
                Available at {item.discounter_count} store{item.discounter_count > 1 ? 's' : ''}
              </p>
              <button
                onClick={() => onViewDetails(item.fragrance.id)}
                className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors"
              >
                Compare Prices
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [filters, setFilters] = useState({ sort_by: 'price_asc', limit: 12, offset: 0 });
  const [brands, setBrands] = useState([]);
  const [discounters, setDiscounters] = useState([]);
  const [selectedFragrance, setSelectedFragrance] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [totalCount, setTotalCount] = useState(0);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [brandsResponse, discountersResponse] = await Promise.all([
        axios.get(`${API_BASE}/brands`),
        axios.get(`${API_BASE}/discounters`)
      ]);
      setBrands(brandsResponse.data);
      setDiscounters(discountersResponse.data);
    } catch (error) {
      console.error('Error loading initial data:', error);
    }
  };

  const handleSearch = async (searchFilters = {}) => {
    setLoading(true);
    const searchParams = { ...filters, ...searchFilters, offset: 0 };
    
    try {
      const response = await axios.get(`${API_BASE}/search`, { params: searchParams });
      setSearchResults(response.data.results);
      setTotalCount(response.data.total_count);
      setFilters(searchParams);
      setShowResults(true);
    } catch (error) {
      console.error('Error searching fragrances:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    handleSearch(newFilters);
  };

  const handleViewDetails = (fragranceId) => {
    const fragrance = searchResults.find(r => r.fragrance.id === fragranceId)?.fragrance ||
                     { id: fragranceId };
    setSelectedFragrance(fragrance);
    setShowModal(true);
  };

  const loadMore = async () => {
    setLoading(true);
    const newOffset = filters.offset + filters.limit;
    const searchParams = { ...filters, offset: newOffset };
    
    try {
      const response = await axios.get(`${API_BASE}/search`, { params: searchParams });
      setSearchResults(prev => [...prev, ...response.data.results]);
      setFilters(searchParams);
    } catch (error) {
      console.error('Error loading more results:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <HeroSection onSearch={handleSearch} />

      {/* Popular Fragrances (shown when not searching) */}
      {!showResults && <PopularSection onViewDetails={handleViewDetails} />}

      {/* Search Results */}
      {showResults && (
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex gap-8">
            {/* Filters Sidebar */}
            <div className="w-80 flex-shrink-0">
              <FilterSidebar
                filters={filters}
                onFilterChange={handleFilterChange}
                brands={brands}
                discounters={discounters}
              />
            </div>

            {/* Results */}
            <div className="flex-1">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  Search Results {totalCount > 0 && `(${totalCount} found)`}
                </h2>
                <button
                  onClick={() => setShowResults(false)}
                  className="text-purple-600 hover:text-purple-700"
                >
                  ← Back to Home
                </button>
              </div>

              {loading && searchResults.length === 0 ? (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
                  <p className="mt-4 text-gray-600">Searching fragrances...</p>
                </div>
              ) : searchResults.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-gray-600">No fragrances found. Try adjusting your filters.</p>
                </div>
              ) : (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {searchResults.map((result, index) => (
                      <ProductCard
                        key={index}
                        result={result}
                        discounters={discounters}
                        onViewDetails={handleViewDetails}
                      />
                    ))}
                  </div>

                  {/* Load More Button */}
                  {searchResults.length < totalCount && (
                    <div className="text-center mt-8">
                      <button
                        onClick={loadMore}
                        disabled={loading}
                        className="bg-purple-600 text-white px-8 py-3 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
                      >
                        {loading ? 'Loading...' : 'Load More'}
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Product Details Modal */}
      <ProductModal
        fragrance={selectedFragrance}
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        discounters={discounters}
      />

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <h3 className="text-2xl font-bold mb-4">Fragrance Discounter Search</h3>
          <p className="text-gray-300 mb-6">
            Find the best deals on designer fragrances from trusted discount retailers
          </p>
          <div className="flex justify-center space-x-8 text-sm text-gray-400">
            <span>Compare prices instantly</span>
            <span>•</span>
            <span>Authentic fragrances only</span>
            <span>•</span>
            <span>Best deals guaranteed</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;