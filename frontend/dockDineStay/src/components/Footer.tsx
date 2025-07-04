// src/components/Footer.tsx
import React from 'react';
import classes from './Footer.module.css';

const Footer: React.FC = () => {
  return (
    <footer className={classes.footer}>
      <div className={classes.footerContent}>
        <p>&copy; {new Date().getFullYear()} DockDineStay. All rights reserved.</p>
        <p>Designed and Developed for a seamless experience.</p>
      </div>
    </footer>
  );
};

export default Footer;