import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "VakeelAI: Legal Assistant for Indian Laws",
  description:
    "Chatbot for Indian law queries using RAG - covering IPC, RTI, labor laws, with multilingual support and citations.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en-IN">
      <head />
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-white text-black`}
      >
        <main>{children}</main>
      </body>
    </html>
  );
}
