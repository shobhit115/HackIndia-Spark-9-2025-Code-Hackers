import Image from "next/image";

const teamMembers = [
  {
    name: "Tushar Saini",
    title: "Backend & AI Model Developer",
    imageUrl:
      "/images/team/tushar.jpg",
  },
  {
    name: "Siddharth Kumar",
    title: "Fontend Developer & Backend Coordinator",
    imageUrl:
      "/images/team/siddharth.jpg",
  },
  {
    name: "Shivam Raj",
    title: "Data & Retrieval Architect",
    imageUrl:
      "/images/team/shivam.jpg",
  },
  {
    name: "Shobhit Singh",
    title: "Legal Research Specialist & AI Model Contributer",
    imageUrl:
      "/images/team/shobhit.jpg",
  },
];

const Team = () => {
  return (
    <div className="flex flex-col items-center justify-center py-14 px-4 sm:px-6 lg:px-8">
      <div className="text-center max-w-xl mx-auto">
        <b className="text-center text-muted-foreground font-semibold text-base">
          🇮🇳 Built for Bharat
        </b>
        <h2 className="mt-3 text-4xl sm:text-5xl font-bold tracking-tight">
          Meet the RAGify India Team
        </h2>
        <p className="mt-4 text-base sm:text-lg">
          We're a passionate crew of developers, legal minds, and AI
          enthusiasts working to make law accessible to every Indian citizen.
        </p>
      </div>
      <div className="mt-20 w-full grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-12 max-w-screen-lg mx-auto">
        {teamMembers.map((member) => (
          <div key={member.name} className="text-center">
            <Image
              src={member.imageUrl}
              alt={member.name}
              className="h-20 w-20 rounded-full object-cover mx-auto bg-secondary"
              width={120}
              height={120}
            />
            <h3 className="mt-4 text-lg font-semibold">{member.name}</h3>
            <p className="text-muted-foreground">{member.title}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Team;
