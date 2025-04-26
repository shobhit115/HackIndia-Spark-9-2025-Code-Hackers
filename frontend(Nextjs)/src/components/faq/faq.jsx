import {
  ShieldCheck,
  Book,
  Info,
  FileText,
  User,
} from "lucide-react";

const faq = [
  {
    icon: Info,
    question: "What is RAGify India?",
    answer:
      "RAGify India is a cutting-edge legal assistant powered by AI, designed to help you navigate Indian laws with ease using advanced search and natural language processing.",
  },
  {
    icon: Book,
    question: "How accurate are the legal answers?",
    answer:
      "RAGify India provides highly accurate legal information sourced from official government legal texts, such as the IPC, RTI, and other major statutes. However, it should not be considered as a substitute for professional legal advice.",
  },
  {
    icon: FileText,
    question: "How do I search for legal information?",
    answer:
      "You can simply type your question or legal query in the search bar, and RAGify India will retrieve relevant legal text, summaries, or detailed information to assist you.",
  },
  {
    icon: ShieldCheck,
    question: "Is my data secure?",
    answer:
      "Yes, your privacy is our priority. We ensure that all your queries are anonymous, and your data is not shared with any third parties without your consent.",
  },
  {
    icon: User,
    question: "Can I get personalized legal advice?",
    answer:
      "RAGify India offers general legal information. For specific and personalized legal advice, we recommend consulting a licensed attorney or legal expert in your area.",
  },
  {
    icon: FileText,
    question: "Which laws can I query in RAGify India?",
    answer:
      "You can query laws related to the Indian Penal Code (IPC), Right to Information (RTI), labor laws, constitutional law, family law, and many more.",
  },
];

const FAQ = () => {
  return (
    <div className="min-h-screen flex items-center justify-center px-6 py-12">
      <div className="max-w-screen-lg">
        <h2 className="text-4xl md:text-5xl !leading-[1.15] font-bold tracking-tighter text-center">
          Frequently Asked Questions
        </h2>
        <p className="mt-3 text-lg text-center text-muted-foreground">
          Quick answers to common legal questions and how RAGify India can help you.
        </p>

        <div className="mt-12 grid md:grid-cols-2 rounded-xl overflow-hidden outline outline-[1px] outline-background outline-offset-[-1px]">
          {faq.map(({ question, answer, icon: Icon }) => (
            <div key={question} className="border p-6 -mt-px -ml-px">
              <div className="h-10 w-10 flex items-center justify-center rounded-full bg-accent">
                <Icon />
              </div>
              <div className="mt-3 mb-2 flex items-start gap-2 text-[1.35rem] font-semibold tracking-tight">
                <span>{question}</span>
              </div>
              <p>{answer}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FAQ;
