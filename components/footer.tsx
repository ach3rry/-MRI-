"use client";

import { motion } from "framer-motion";
import { Github, Mail, FileText } from "lucide-react";

export function Footer() {
  return (
    <footer className="py-16 px-6 border-t border-border">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="flex flex-col md:flex-row items-center justify-between gap-8"
        >
          {/* Logo and description */}
          <div className="text-center md:text-left">
            <div className="text-2xl font-bold gradient-text mb-2">
              膝影智析
            </div>
            <p className="text-sm text-muted-foreground max-w-md">
              面向MLLM的医疗多模态自动化预处理与标注系统
            </p>
            <p className="text-xs text-muted-foreground mt-2">
              计算机设计大赛参赛作品
            </p>
          </div>

          {/* Links */}
          <div className="flex items-center gap-4">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-muted hover:bg-muted/80 transition-colors text-sm"
            >
              <Github className="w-4 h-4" />
              <span>源代码</span>
            </a>
            <a
              href="#"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-muted hover:bg-muted/80 transition-colors text-sm"
            >
              <FileText className="w-4 h-4" />
              <span>文档</span>
            </a>
            <a
              href="mailto:contact@example.com"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-muted hover:bg-muted/80 transition-colors text-sm"
            >
              <Mail className="w-4 h-4" />
              <span>联系</span>
            </a>
          </div>
        </motion.div>

        {/* Copyright */}
        <div className="mt-12 pt-8 border-t border-border text-center text-sm text-muted-foreground">
          <p>&copy; 2025 膝影智析团队. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
