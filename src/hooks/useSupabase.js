// TURSAKUR 2.0 - Custom Hooks for Supabase Data
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { healthFacilitiesAPI } from '../lib/supabase'

// Hook for getting all health facilities
export const useHealthFacilities = (filters = {}) => {
  return useQuery({
    queryKey: ['health-facilities', filters],
    queryFn: () => healthFacilitiesAPI.getAll(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  })
}

// Hook for getting provinces
export const useProvinces = () => {
  return useQuery({
    queryKey: ['provinces'],
    queryFn: () => healthFacilitiesAPI.getProvinces(),
    staleTime: 30 * 60 * 1000, // 30 minutes
    cacheTime: 60 * 60 * 1000, // 1 hour
  })
}

// Hook for getting facility types
export const useFacilityTypes = () => {
  return useQuery({
    queryKey: ['facility-types'],
    queryFn: () => healthFacilitiesAPI.getFacilityTypes(),
    staleTime: 30 * 60 * 1000, // 30 minutes
    cacheTime: 60 * 60 * 1000, // 1 hour
  })
}

// Hook for getting statistics
export const useStatistics = () => {
  return useQuery({
    queryKey: ['statistics'],
    queryFn: () => healthFacilitiesAPI.getStatistics(),
    staleTime: 15 * 60 * 1000, // 15 minutes
    cacheTime: 30 * 60 * 1000, // 30 minutes
  })
}

// Hook for search functionality
export const useSearch = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ query, filters }) => {
      if (!query || query.length < 2) {
        return healthFacilitiesAPI.getAll(filters)
      }
      
      return healthFacilitiesAPI.getAll({
        ...filters,
        search: query
      })
    },
    onSuccess: (data, variables) => {
      // Update the cache with search results
      queryClient.setQueryData(
        ['health-facilities', { ...variables.filters, search: variables.query }],
        data
      )
    }
  })
}

// Hook for filtering facilities
export const useFilters = () => {
  const queryClient = useQueryClient()
  
  const clearCache = () => {
    queryClient.invalidateQueries({ queryKey: ['health-facilities'] })
  }
  
  const prefetchFiltered = async (filters) => {
    await queryClient.prefetchQuery({
      queryKey: ['health-facilities', filters],
      queryFn: () => healthFacilitiesAPI.getAll(filters),
      staleTime: 5 * 60 * 1000,
    })
  }
  
  return {
    clearCache,
    prefetchFiltered
  }
}
