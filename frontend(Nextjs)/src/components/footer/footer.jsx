import { Separator } from "@/components/ui/separator";
import Link from "next/link";

const Footer = () => {
  return (
    <div className="flex flex-col items-center justify-center">
    <footer className="w-full">
      <div className="max-w-screen-xl mx-auto w-full">
        <Separator />
        <div
          className="py-8 flex flex-col items-center justify-center gap-y-4 px-6 xl:px-0 text-center"
        >
          {/* Copyright */}
          <span className="text-muted-foreground">
            &copy; {new Date().getFullYear()}{" "}
            <Link href="/" target="_blank" rel="noopener noreferrer">
              VakeelAI
            </Link>
            . All rights reserved.
          </span>
        </div>
      </div>
    </footer>
  </div>
  
  );
};

export default Footer;
