import { Header } from "@/components/header";
import { Hero } from "@/components/hero";
import { Features } from "@/components/features";
import { Pipeline } from "@/components/pipeline";
import { Labels } from "@/components/labels";
import { TechStack } from "@/components/tech-stack";
import { Footer } from "@/components/footer";

export default function Home() {
  return (
    <main className="min-h-screen">
      <Header />
      <Hero />
      <Features />
      <Pipeline />
      <Labels />
      <TechStack />
      <Footer />
    </main>
  );
}
