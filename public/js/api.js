/**
 * TURSAKUR API - Türkiye Sağlık Kuruluşları API
 * RESTful API endpoints for healthcare institutions data
 */

class TURSAKUR_API {
    constructor() {
        this.baseURL = window.location.origin;
        this.dataURL = `${this.baseURL}/data/turkiye_saglik_kuruluslari.json`;
        this.version = 'v1';
    }

    /**
     * Initialize API endpoints
     */
    init() {
        // API route handling
        this.setupRoutes();
        console.log('🚀 TURSAKUR API initialized');
    }

    /**
     * Setup API routes
     */
    setupRoutes() {
        // Listen for API requests
        if (window.location.pathname.startsWith('/api/')) {
            this.handleAPIRequest();
        }
    }

    /**
     * Handle API requests
     */
    async handleAPIRequest() {
        const path = window.location.pathname;
        const searchParams = new URLSearchParams(window.location.search);

        try {
            let response;
            
            if (path === '/api/v1/institutions') {
                response = await this.getInstitutions(searchParams);
            } else if (path.match(/^\/api\/v1\/institutions\/(.+)$/)) {
                const id = path.match(/^\/api\/v1\/institutions\/(.+)$/)[1];
                response = await this.getInstitutionById(id);
            } else if (path === '/api/v1/provinces') {
                response = await this.getProvinces();
            } else if (path === '/api/v1/types') {
                response = await this.getInstitutionTypes();
            } else if (path === '/api/v1/stats') {
                response = await this.getStatistics();
            } else {
                response = this.getAPIInfo();
            }

            this.sendJSONResponse(response);
        } catch (error) {
            this.sendErrorResponse(error.message, 500);
        }
    }

    /**
     * Get all institutions with optional filtering
     */
    async getInstitutions(params) {
        const data = await this.loadData();
        let institutions = data.kurumlar;

        // Apply filters
        const province = params.get('province');
        const type = params.get('type');
        const search = params.get('search');
        const limit = parseInt(params.get('limit')) || 50;
        const offset = parseInt(params.get('offset')) || 0;

        if (province) {
            institutions = institutions.filter(inst => 
                inst.il_adi.toLowerCase().includes(province.toLowerCase())
            );
        }

        if (type) {
            institutions = institutions.filter(inst => 
                inst.kurum_tipi.toLowerCase().includes(type.toLowerCase())
            );
        }

        if (search) {
            institutions = institutions.filter(inst => 
                inst.kurum_adi.toLowerCase().includes(search.toLowerCase()) ||
                inst.il_adi.toLowerCase().includes(search.toLowerCase()) ||
                inst.ilce_adi.toLowerCase().includes(search.toLowerCase())
            );
        }

        // Pagination
        const total = institutions.length;
        const paginatedInstitutions = institutions.slice(offset, offset + limit);

        return {
            data: paginatedInstitutions,
            meta: {
                total,
                limit,
                offset,
                has_more: offset + limit < total
            }
        };
    }

    /**
     * Get institution by ID
     */
    async getInstitutionById(id) {
        const data = await this.loadData();
        const institution = data.kurumlar.find(inst => inst.kurum_id === id);

        if (!institution) {
            throw new Error('Institution not found');
        }

        return { data: institution };
    }

    /**
     * Get all provinces
     */
    async getProvinces() {
        const data = await this.loadData();
        const provinces = [...new Set(data.kurumlar.map(inst => inst.il_adi))].sort();

        return {
            data: provinces.map(province => ({
                name: province,
                count: data.kurumlar.filter(inst => inst.il_adi === province).length
            }))
        };
    }

    /**
     * Get all institution types
     */
    async getInstitutionTypes() {
        const data = await this.loadData();
        const types = [...new Set(data.kurumlar.map(inst => inst.kurum_tipi))].sort();

        return {
            data: types.map(type => ({
                name: type,
                count: data.kurumlar.filter(inst => inst.kurum_tipi === type).length,
                color: data.kurumlar.find(inst => inst.kurum_tipi === type)?.kurum_tipi_renk || '#424242'
            }))
        };
    }

    /**
     * Get statistics
     */
    async getStatistics() {
        const data = await this.loadData();
        const institutions = data.kurumlar;

        return {
            data: {
                total_institutions: institutions.length,
                total_provinces: new Set(institutions.map(inst => inst.il_adi)).size,
                total_types: new Set(institutions.map(inst => inst.kurum_tipi)).size,
                institutions_with_phone: institutions.filter(inst => inst.telefon && inst.telefon.trim()).length,
                institutions_with_website: institutions.filter(inst => inst.web_sitesi && inst.web_sitesi.trim()).length,
                institutions_with_coordinates: institutions.filter(inst => inst.koordinat_lat && inst.koordinat_lon).length,
                last_updated: data.meta.last_updated
            }
        };
    }

    /**
     * Get API information
     */
    getAPIInfo() {
        return {
            name: 'TURSAKUR API',
            version: this.version,
            description: 'Türkiye Sağlık Kuruluşları Açık Veritabanı API',
            endpoints: {
                'GET /api/v1/institutions': 'Get all institutions (supports filtering)',
                'GET /api/v1/institutions/{id}': 'Get institution by ID',
                'GET /api/v1/provinces': 'Get all provinces with counts',
                'GET /api/v1/types': 'Get all institution types with counts',
                'GET /api/v1/stats': 'Get database statistics'
            },
            parameters: {
                'province': 'Filter by province name',
                'type': 'Filter by institution type',
                'search': 'Search in institution name, province, or district',
                'limit': 'Limit number of results (default: 50, max: 1000)',
                'offset': 'Offset for pagination (default: 0)'
            },
            examples: [
                '/api/v1/institutions?province=istanbul&limit=10',
                '/api/v1/institutions?type=özel hastane',
                '/api/v1/institutions?search=üniversite&limit=20',
                '/api/v1/institutions/TR-34-OH-001'
            ]
        };
    }

    /**
     * Load data from JSON file
     */
    async loadData() {
        if (this.cachedData) {
            return this.cachedData;
        }

        const response = await fetch(this.dataURL);
        if (!response.ok) {
            throw new Error('Failed to load data');
        }

        this.cachedData = await response.json();
        return this.cachedData;
    }

    /**
     * Send JSON response
     */
    sendJSONResponse(data) {
        // In a real implementation, this would set proper headers and send response
        // For client-side demo, we'll log to console and show in page
        const jsonResponse = JSON.stringify(data, null, 2);
        console.log('API Response:', jsonResponse);
        
        // Show API response in page
        document.body.innerHTML = `
            <div style="font-family: monospace; padding: 20px; background: #f5f5f5; white-space: pre-wrap;">
                ${jsonResponse}
            </div>
        `;
    }

    /**
     * Send error response
     */
    sendErrorResponse(message, status = 400) {
        const errorResponse = {
            error: {
                message,
                status,
                timestamp: new Date().toISOString()
            }
        };
        
        this.sendJSONResponse(errorResponse);
    }
}

// Global API instance
const tursakurAPI = new TURSAKUR_API();

// Initialize API if on API route
if (window.location.pathname.startsWith('/api/')) {
    tursakurAPI.init();
}

// Expose API for external use
window.TURSAKUR_API = tursakurAPI;
