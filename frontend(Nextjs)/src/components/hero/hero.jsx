"use client";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { BackgroundPattern } from "@/custom-components/background-pattern";
import { ArrowUpRight, CirclePlay, Scale } from "lucide-react";
import React from "react";

const Hero = () => {

  const handleTryClick = () => {
    window.location.href = "/assistant";
  };


  return (
    <div
      className="min-h-screen flex items-center justify-center overflow-hidden"
    >
      <div className="max-w-screen-xl w-full mx-auto grid lg:grid-cols-2 gap-12 px-6 py-12 lg:py-0">
        <BackgroundPattern />
        <div className="my-auto">
          <Badge className="bg-gradient-to-br via-70% from-primary via-muted/30 to-primary rounded-full py-1 border-none">
            🔍 Ask Anything – Indian Law
          </Badge>
          <h1 className="mt-6 max-w-[17ch] text-4xl md:text-5xl lg:text-[2.75rem] xl:text-5xl font-bold !leading-[1.2] tracking-tight">
            RAGify India – Your Legal Assistant
          </h1>
          <p className="mt-6 max-w-[60ch] text-lg">
            Get instant answers about Indian laws like IPC, RTI, and labor
            regulations. Powered by Retrieval-Augmented Generation (RAG) with
            multilingual support and legal citations.
          </p>
          <div className="mt-12 flex items-center gap-4">
          <Button size="lg" onClick={handleTryClick} className="rounded-full text-base">
                  Try the Assistant <ArrowUpRight className="!h-5 !w-5 ml-2" />
                </Button>
          </div>
        </div>
        <div className="w-full flex items-center justify-center">
          <img
            src="/images/mainImage.jpg"
            alt="Legal Assistant Illustration"
            className="w-full max-w-md lg:max-w-xl rounded-xl shadow-md"
          />
        </div>
      </div>
    </div>
  );
};

export default Hero;
