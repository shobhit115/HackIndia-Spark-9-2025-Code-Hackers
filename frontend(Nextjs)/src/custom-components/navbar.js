"use client";
import {
  ArrowUpRight,
  Menu,
  Scale,
} from "lucide-react";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "@/components/ui/navigation-menu";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";

const Navbar1 = ({
  logo = {
    url: "http://localhost:3000",
    // src: "https://shadcnblocks.com/images/block/logos/shadcnblockscom-icon.svg",
    alt: "logo",
    title: "VakeelAI",
  },
  menu = [
    { title: "Highlights", url: "#highlights" },
    { title: "Team", url: "#team" },
    { title: "Insights", url: "#stats" },
    {
      title: "FAQs",
      url: "#faq",
    },
  ],
}) => {
  const handleTryClick = () => {
    window.location.href = "/assistant";
  };

  return (
    <section className="sticky top-0 z-50 bg-white py-3 border-b">
      <div className="container mx-auto px-4">
        {/* Desktop Navigation */}
        <div className="hidden lg:flex justify-center">
          <nav className="flex justify-between items-center w-full max-w-7xl">
            {/* Logo */}
            <a href={logo.url} className="flex items-center gap-2">
              {/* <img src={logo.src} className="max-h-8" alt={logo.alt} /> */}
              <Scale />
              <span className="text-lg font-semibold tracking-tight">
                {logo.title}
              </span>
            </a>

            {/* Navigation Menu */}
            <NavigationMenu>
              <NavigationMenuList>
                {menu.map((item) => renderMenuItem(item))}
                <Button
                  size="lg"
                  onClick={handleTryClick}
                  className="rounded-full text-base ml-4"
                >
                  Try It <ArrowUpRight className="!h-5 !w-5 ml-2" />
                </Button>
              </NavigationMenuList>
            </NavigationMenu>
          </nav>
        </div>

        {/* Mobile Navigation */}
        <div className="flex lg:hidden items-center justify-between py-2">
          {/* Logo */}
          <a href={logo.url} className="flex items-center gap-2">
            <Scale />
            {/* <img src={logo.src} className="max-h-8" alt={logo.alt} /> */}
            <span className="text-lg font-semibold tracking-tight">
              {logo.title}
            </span>
          </a>

          {/* Mobile Menu Button */}
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="outline" size="icon">
                <Menu className="w-5 h-5" />
              </Button>
            </SheetTrigger>
            <SheetContent className="overflow-y-auto">
              <SheetHeader>
                <SheetTitle>
                  <a href={logo.url} className="flex items-center gap-2">
                    <Scale />
                    {/* <img src={logo.src} className="max-h-8" alt={logo.alt} /> */}
                  </a>
                </SheetTitle>
              </SheetHeader>
              <div className="p-4">
                <Accordion
                  type="single"
                  collapsible
                  className="flex w-full flex-col gap-4"
                >
                  {menu.map((item) => renderMobileMenuItem(item))}
                  <Button
                    size="lg"
                    onClick={handleTryClick}
                    className="rounded-full text-base"
                  >
                    Try It <ArrowUpRight className="!h-5 !w-5 ml-2" />
                  </Button>
                </Accordion>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </section>
  );
};

const renderMenuItem = (item) => {
  if (item.items) {
    return (
      <NavigationMenuItem key={item.title}>
        <NavigationMenuTrigger>{item.title}</NavigationMenuTrigger>
        <NavigationMenuContent className="bg-popover text-popover-foreground">
          {item.items.map((subItem) => (
            <NavigationMenuLink asChild key={subItem.title} className="w-80">
              <SubMenuLink item={subItem} />
            </NavigationMenuLink>
          ))}
        </NavigationMenuContent>
      </NavigationMenuItem>
    );
  }

  return (
    <NavigationMenuItem key={item.title}>
      <NavigationMenuLink
        href={item.url}
        className="group inline-flex h-10 w-max items-center justify-center rounded-md bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-muted hover:text-accent-foreground"
      >
        {item.title}
      </NavigationMenuLink>
    </NavigationMenuItem>
  );
};

const renderMobileMenuItem = (item) => {
  if (item.items) {
    return (
      <AccordionItem key={item.title} value={item.title} className="border-b-0">
        <AccordionTrigger className="text-md py-0 font-semibold hover:no-underline">
          {item.title}
        </AccordionTrigger>
        <AccordionContent className="mt-2">
          {item.items.map((subItem) => (
            <SubMenuLink key={subItem.title} item={subItem} />
          ))}
        </AccordionContent>
      </AccordionItem>
    );
  }

  return (
    <a key={item.title} href={item.url} className="text-md font-semibold">
      {item.title}
    </a>
  );
};

const SubMenuLink = ({ item }) => {
  return (
    <a
      className="flex flex-row gap-4 rounded-md p-3 leading-none no-underline transition-colors outline-none select-none hover:bg-muted hover:text-accent-foreground"
      href={item.url}
    >
      <div className="text-foreground">{item.icon}</div>
      <div>
        <div className="text-sm font-semibold">{item.title}</div>
        {item.description && (
          <p className="text-sm leading-snug text-muted-foreground">
            {item.description}
          </p>
        )}
      </div>
    </a>
  );
};

export { Navbar1 };
