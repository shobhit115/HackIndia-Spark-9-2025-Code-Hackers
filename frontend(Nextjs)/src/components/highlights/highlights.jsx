import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  BookText,
  Languages,
  Scale,
  ScrollText,
  SearchCheck,
  MessageCircleQuestion,
} from "lucide-react";

const features = [
  {
    icon: SearchCheck,
    title: "Instant Legal Lookup",
    description:
      "Quickly find legal sections from IPC, RTI, labor laws, and more, using natural language queries.",
  },
  {
    icon: Scale,
    title: "Reliable Legal Citations",
    description:
      "Every answer includes source citations from trusted government databases like India Code.",
  },
  {
    icon: Languages,
    title: "Multi-Lingual Support",
    description:
      "Ask legal questions in Hindi, Tamil, Bengali, or English — the assistant speaks your language.",
  },
  {
    icon: ScrollText,
    title: "Acts & Sections Explained",
    description:
      "Understand complex legal jargon with plain-language explanations and contextual info.",
  },
  {
    icon: BookText,
    title: "Ask About Rights",
    description:
      "Know your rights as a citizen, employee, or consumer — get precise legal answers instantly.",
  },
  {
    icon: MessageCircleQuestion,
    title: "Chat-Based Interaction",
    description:
      "Engage in a smooth conversational flow with the assistant to ask follow-ups or clarify answers.",
  },
];

const Highlights = () => {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="max-w-screen-lg w-full py-12 px-6">
        <h2 className="text-4xl md:text-5xl md:leading-[3.5rem] font-bold tracking-tight max-w-2xl">
          Powerful Features for Legal Assistance
        </h2>
        <div className="mt-6 md:mt-8 w-full mx-auto grid md:grid-cols-2 gap-12">
          <div>
            <Accordion defaultValue="item-0" type="single" className="w-full">
              {features.map(({ title, description, icon: Icon }, index) => (
                <AccordionItem
                  key={index}
                  value={`item-${index}`}
                  className="data-[state=open]:border-b-2 data-[state=open]:border-primary"
                >
                  <AccordionTrigger className="text-lg [&>svg]:hidden">
                    <div className="flex items-center gap-4">
                      <Icon />
                      {title}
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="text-[17px] leading-relaxed text-muted-foreground">
                    {description}
                    <div className="mt-6 mb-2 md:hidden aspect-video w-full bg-muted rounded-xl" />
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </div>

          {/* Media / Visual Block */}
          <div className="aspect-[4/4] w-full">
  <img
    src="/images/law-ai.webp"
    alt="Legal Features"
    className="rounded-md shadow object-cover w-full h-full"
  />
</div>
        </div>
      </div>
    </div>
  );
};

export default Highlights;
