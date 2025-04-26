import FAQ from "@/components/faq/faq";
import Highlights from "@/components/highlights/highlights";
import Footer from "@/components/footer/footer";
import Hero from "@/components/hero/hero";
import Stats from "@/components/stats/stats";
import Team from "@/components/team/team";
import { Navbar1 } from "@/custom-components/navbar";

export default function Home() {
  return (
    <div>
      <Navbar1 />

      {/* Hero Section */}
      <Hero />

      {/* Features Section */}
      <div id="highlights" className="py-8" >
        <Highlights />
      </div>

      {/* Team Section */}
      <div id="team" className="py-8" >
        <Team />
      </div>

      {/* Stats Section */}
      <div id="stats" className="py-4" >
        <Stats />
      </div>
      
      {/* FAQ Section */}
      <div id="faq" className="py-4" >
        <FAQ />
      </div>

      {/* Footer Section */}
      <div id="footer" className="py-8" >
        <Footer />
      </div>
    </div>
  );
}
