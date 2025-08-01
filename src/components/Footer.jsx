import React from 'react';
import './Footer.css';

/**
 * Material Design 3 Footer Component
 * Site alt bilgileri ve bağlantılar
 */
function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-content">
        {/* Ana Footer İçeriği */}
        <div className="footer-main">
          <div className="footer-section">
            <div className="footer-brand">
              <img 
                src="/assets/logos/TURSAKUR-Color.png" 
                alt="TURSAKUR" 
                className="footer-logo"
              />
              <p className="body-medium footer-description">
                Türkiye'deki tüm sağlık kuruluşlarını kolayca bulabileceğiniz 
                kapsamlı rehber platformu.
              </p>
            </div>
          </div>

          <div className="footer-section">
            <h3 className="title-small footer-title">Keşfet</h3>
            <ul className="footer-links">
              <li><a href="/" className="footer-link">Ana Sayfa</a></li>
              <li><a href="/harita" className="footer-link">Harita</a></li>
              <li><a href="/arama" className="footer-link">Gelişmiş Arama</a></li>
              <li><a href="/istatistikler" className="footer-link">İstatistikler</a></li>
            </ul>
          </div>

          <div className="footer-section">
            <h3 className="title-small footer-title">Destek</h3>
            <ul className="footer-links">
              <li><a href="/hakkinda" className="footer-link">Hakkında</a></li>
              <li><a href="/iletisim" className="footer-link">İletişim</a></li>
              <li><a href="/yardim" className="footer-link">Yardım</a></li>
              <li><a href="/geri-bildirim" className="footer-link">Geri Bildirim</a></li>
            </ul>
          </div>

          <div className="footer-section">
            <h3 className="title-small footer-title">Yasal</h3>
            <ul className="footer-links">
              <li><a href="/gizlilik" className="footer-link">Gizlilik Politikası</a></li>
              <li><a href="/kullanim-kosullari" className="footer-link">Kullanım Koşulları</a></li>
              <li><a href="/cerez-politikasi" className="footer-link">Çerez Politikası</a></li>
              <li><a href="/veri-kaynaklari" className="footer-link">Veri Kaynakları</a></li>
            </ul>
          </div>
        </div>

        {/* Alt Bar */}
        <div className="footer-bottom">
          <div className="footer-bottom-content">
            <p className="body-small footer-copyright">
              © {currentYear} TURSAKUR. Tüm hakları saklıdır.
            </p>
            <div className="footer-social">
              <p className="body-small">
                Açık kaynak projesi • MIT Lisansı
              </p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
