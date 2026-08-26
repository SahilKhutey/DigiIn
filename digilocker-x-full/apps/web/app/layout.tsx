import React from "react";
import "./globals.css";

export const metadata = {
  title: "DigiLocker X",
  description: "Citizen documents, credentials and verification",
};

export default function RootLayout({children}:{children:React.ReactNode}) {
  return <html lang="en"><body>{children}</body></html>;
}
