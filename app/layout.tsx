import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
});

export const metadata: Metadata = {
  title: "膝影智析 | 面向MLLM的医疗多模态自动化预处理与标注系统",
  description: "基于Qwen3-VL的膝关节MRI图像自动化预处理与标注系统，实现端到端的医学影像数据处理流水线，支持40+结构化医学标签生成，降低90%标注成本。",
  keywords: ["MRI", "医学影像", "深度学习", "多模态大模型", "MLLM", "膝关节", "自动标注"],
  authors: [{ name: "膝影智析团队" }],
};

export const viewport: Viewport = {
  themeColor: "#0a0a0a",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased`}>
        {children}
      </body>
    </html>
  );
}
