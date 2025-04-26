import React from "react";

const Stats = () => {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="max-w-screen-xl mx-auto w-full py-12 px-6 xl:px-0">
        <h2 className="text-4xl md:text-5xl font-bold tracking-tight">
          Making Indian Law Accessible with AI
        </h2>
        <p className="mt-6 text-lg max-w-2xl text-foreground/70">
          RAGify India uses cutting-edge Retrieval-Augmented Generation to help
          citizens, professionals, and students understand Indian laws — fast,
          accurate, and in your language.
        </p>

        <div className="mt-16 sm:mt-24 grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-x-10 gap-y-16 justify-center">
          <div>
            <span className="text-5xl md:text-6xl font-bold text-indigo-600">
              10,000+
            </span>
            <p className="mt-6 font-semibold text-xl">
              Legal Sections Indexed
            </p>
            <p className="mt-2 text-[17px] text-muted-foreground">
              Covering IPC, RTI, labor laws, and more from official government
              sources.
            </p>
          </div>
          <div>
            <span className="text-5xl md:text-6xl font-bold text-green-500">
              12
            </span>
            <p className="mt-6 font-semibold text-xl">Languages Supported</p>
            <p className="mt-2 text-[17px] text-muted-foreground">
              Ask your questions in Hindi, Tamil, Bengali, Marathi, and more.
            </p>
          </div>
          <div>
            <span className="text-5xl md:text-6xl font-bold text-rose-600">
              2s
            </span>
            <p className="mt-6 font-semibold text-xl">Avg. Response Time</p>
            <p className="mt-2 text-[17px] text-muted-foreground">
              Get near-instant answers backed by retrieval and generation.
            </p>
          </div>
          <div>
            <span className="text-5xl md:text-6xl font-bold text-yellow-500">
              35+
            </span>
            <p className="mt-6 font-semibold text-xl">Indian Laws Covered</p>
            <p className="mt-2 text-[17px] text-muted-foreground">
              Including labor, civil, constitutional, and criminal law domains.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Stats;
