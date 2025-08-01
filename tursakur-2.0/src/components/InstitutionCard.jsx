import React from 'react'
import './InstitutionCard.css'

function InstitutionCard({ institution, searchQuery = "", className = "" }) {
  const { 
    id, 
    isim_standart, 
    tip, 
    adres_yapilandirilmis, 
    iletisim, 
    meta_veri,
    kaynaklar 
  } = institution

  // Arama terimini vurgula
  const highlightText = (text, query) => {
    if (!query || !text) return text
    
    const regex = new RegExp(`(${query})`, 'gi')
    const parts = text.split(regex)
    
    return parts.map((part, index) => 
      regex.test(part) ? 
        <mark key={index} className="highlight">{part}</mark> : 
        part
    )
  }

  // Kurum tipine göre ikon
  const getTypeIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'devlet hastanesi':
      case 'kamu hastanesi':
        return '🏥'
      case 'özel hastane':
        return '🏢'
      case 'üniversite hastanesi':
        return '🎓'
      case 'ağız ve diş sağlığı merkezi':
        return '🦷'
      case 'aile sağlığı merkezi':
        return '👨‍⚕️'
      default:
        return '🏥'
    }
  }

  // Adres bilgisi
  const address = adres_yapilandirilmis
  const fullAddress = [
    address?.mahalle,
    address?.ilce,
    address?.il
  ].filter(Boolean).join(', ')

  // İletişim bilgileri
  const phone = iletisim?.telefon_1
  const website = iletisim?.website

  // Meta bilgiler
  const hasInsurance = meta_veri?.sgk_anlasmasi
  const departments = meta_veri?.bolumler || []

  // Veri kaynağı
  const lastSource = kaynaklar?.[kaynaklar.length - 1]

  return (
    <article className={`institution-card ${className}`}>
      <div className="card-header">
        <div className="institution-info">
          <div className="institution-name-section">
            <span className="type-icon" aria-hidden="true">
              {getTypeIcon(tip)}
            </span>
            <h3 className="institution-name title-medium">
              {highlightText(isim_standart, searchQuery)}
            </h3>
          </div>
          
          {tip && (
            <span className="institution-type label-medium">
              {tip}
            </span>
          )}
        </div>

        {hasInsurance && (
          <div className="sgk-badge" title="SGK Anlaşmalı">
            <span className="label-small">SGK</span>
          </div>
        )}
      </div>

      <div className="card-content">
        {/* Adres */}
        {fullAddress && (
          <div className="address-section">
            <span className="address-icon" aria-hidden="true">📍</span>
            <p className="address body-small">
              {highlightText(fullAddress, searchQuery)}
            </p>
          </div>
        )}

        {/* Departmanlar (ilk 3 tanesi) */}
        {departments.length > 0 && (
          <div className="departments-section">
            <span className="departments-icon" aria-hidden="true">🩺</span>
            <div className="departments">
              {departments.slice(0, 3).map((dept, index) => (
                <span key={index} className="department-chip label-small">
                  {dept}
                </span>
              ))}
              {departments.length > 3 && (
                <span className="more-departments label-small">
                  +{departments.length - 3} daha
                </span>
              )}
            </div>
          </div>
        )}

        {/* Veri kaynağı ve güncellenme */}
        {lastSource && (
          <div className="source-info">
            <span className="source-text label-small">
              Kaynak: {lastSource.kaynak_id}
            </span>
          </div>
        )}
      </div>

      <div className="card-actions">
        {/* Telefon */}
        {phone && (
          <a 
            href={`tel:${phone}`}
            className="action-button phone-button"
            title="Telefon et"
            aria-label={`${isim_standart} kurumunu ara`}
          >
            <span className="action-icon">📞</span>
            <span className="action-text label-medium">Ara</span>
          </a>
        )}

        {/* Web Sitesi */}
        {website && (
          <a 
            href={website}
            target="_blank"
            rel="noopener noreferrer"
            className="action-button website-button"
            title="Web sitesini ziyaret et"
            aria-label={`${isim_standart} web sitesini ziyaret et`}
          >
            <span className="action-icon">🌐</span>
            <span className="action-text label-medium">Web</span>
          </a>
        )}

        {/* Detaylar */}
        <a 
          href={`/kurum/${id}`}
          className="action-button details-button primary"
          aria-label={`${isim_standart} detaylarını görüntüle`}
        >
          <span className="action-text label-medium">Detaylar</span>
          <span className="action-icon">→</span>
        </a>
      </div>
    </article>
  )
}

export default InstitutionCard
