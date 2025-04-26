"use client";

import { useRef, useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Textarea } from "@/components/ui/textarea";
import { Loader2 } from "lucide-react";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";

export default function AIChatbotScreen() {
  const [language, setLanguage] = useState("English");
  const [legalArea, setLegalArea] = useState("");
  const [userType, setUserType] = useState("common");
  const [file, setFile] = useState(null);
  const [fileError, setFileError] = useState("");
  const [chatStarted, setChatStarted] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");
  const fileInputRef = useRef();
  const messagesEndRef = useRef(null);
  const scrollAreaRef = useRef(null);

  // Smooth scroll handling
  useEffect(() => {
    const scrollEl = scrollAreaRef.current;
    if (scrollEl) {
      const shouldScroll =
        scrollEl.scrollTop + scrollEl.clientHeight >=
        scrollEl.scrollHeight - 50;
      if (shouldScroll) {
        scrollEl.scrollTo({
          top: scrollEl.scrollHeight,
          behavior: "smooth",
        });
      }
    }
  }, [messages, loading]);

  const LANGUAGES = [
    { value: "English", label: "English" },
    { value: "Hindi", label: "हिन्दी" },
    { value: "Bengali", label: "বাংলা" },
    { value: "Telugu", label: "తెలుగు" },
    { value: "Tamil", label: "தமிழ்" },
    { value: "Marathi", label: "मराठी" },
    { value: "Gujarati", label: "ગુજરાતી" },
    { value: "Kannada", label: "ಕನ್ನಡ" },
    { value: "Malayalam", label: "മലയാളം" },
    { value: "Punjabi", label: "ਪੰਜਾਬੀ" },
    { value: "Odia", label: "ଓଡ଼ିଆ" },
    { value: "Assamese", label: "অসমীয়া" },
  ];

  const USERTYPES = [
    { value: "common", label: "Common User" },
    { value: "advocate", label: "Advocate" },
    { value: "judge", label: "Judge" }
  ];

  const LEGAL_AREAS = [
    { value: "IPC", label: "IPC" },
    { value: "RTI", label: "RTI" },
    { value: "Labor", label: "Labor Laws" },
    { value: "Other", label: "Other" },
  ];

  function handleFileChange(e) {
    const f = e.target.files[0];
    if (f && f.size > 5 * 1024 * 1024) {
      setFileError("File size exceeds 5MB.");
      setFile(null);
    } else {
      setFileError("");
      setFile(f);
    }
  }

  function handleStartChat() {
    if (!language || !legalArea || !userType) {
      return setApiError("Please fill all filters");
    }
    setApiError("");
    setChatStarted(true);
  }

  async function handleSend() {
    if (!input.trim()) return;
    setLoading(true);
    setApiError("");

    try {
      // Add user message immediately
      const userMessage = { role: "user", content: input };
      setMessages((prev) => [...prev, userMessage]);
      setInput("");

      // setMessages((prev) => [
      //   ...prev,
      //   {
      //     role: "ai",
      //     content: `
      //     Yeah <strong>Great</strong> Choice.
      //     `,
      //   },
      // ]);
      // return;

      // Prepare message history including new message
      const messageHistory = [...messages, userMessage];

      /*
      curl -X POST "http://30.30.20.111:8000/query" -H "Content-Type: application/json" -d 
      "{\
        "question\":\"What is an FIR under the IPC?\",\
        "user_type\":\"Advocate\",\
        "legal_area\":\"Criminal Law\",\
        "selected_language\":\"English\",\
        "history_pq\":\"Explain IPC Section 154\"
      }"
      {{ role: "ai", content: data.reply },{ role: "ai", content: data.reply }}
      */

 
    // Prepare data
    let data;
    let headers = {};

    if (file) {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("payload", JSON.stringify({
            question: input,
            selected_language: language,
            legal_area: legalArea,
            user_type: userType,
            history_pq: JSON.stringify(messageHistory)
        }));
        data = formData;
    } else {
        headers['Content-Type'] = 'application/json';
        data = JSON.stringify({
            question: input,
            selected_language: language,
            legal_area: legalArea,
            user_type: userType,
            history_pq: JSON.stringify(messageHistory)
        });
    }

    const res = await fetch("http://localhost:8080/query", {
      method: "POST",
      headers: headers,
      body: data,
  });


      console.log(res.body);

      if (res.ok) {
        // Parse success response
        try {
          data = await res.json();
          setMessages((prev) => [...prev, { role: "ai", data_source:data.source, content: data.ai_answer }]);
        } catch (jsonError) {
          console.error("JSON Parsing Error:", jsonError);
          throw new Error("Invalid response format from server");
        }
      } else {
        // Handle error responses
        let errorMsg = "Request failed";
        try {
          const errorData = await res.json();
          errorMsg = errorData.error || errorMsg;
        } catch {
          // If response isn't JSON, read as text
          const textData = await res.text();
          errorMsg = textData.startsWith("<")
            ? "Server error occurred. Please try again later."
            : textData || errorMsg;
        }
        throw new Error(errorMsg);
      }
    } catch (err) {
      console.error("API Error:", err);
      setApiError(
        err.message || "Failed to process your request. Please try again."
      );
      // Remove last user message if error occurred
      setMessages((prev) => prev.filter((m, i) => i !== prev.length - 1));
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!loading) handleSend();
    }
  }

  function handleReset() {
    setMessages([]);
    setInput("");
    setFile(null);
    setFileError("");
    setApiError("");
    setChatStarted(false);
    setLegalArea("");
    setUserType("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // ... (keep all existing handler functions)

  return (
    <div className="min-h-screen bg-gradient-to-r from-zinc-400 via-zinc-700 to-zinc-400">
      {!chatStarted ? (
        <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <Card className="border">
            <CardContent className="p-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-8">
                Legal Chatbot
              </h2>

              <div className="space-y-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-gray-700">
                      Language
                    </Label>
                    <Select value={language} onValueChange={setLanguage}>
                      <SelectTrigger className="border-gray-300 hover:border-gray-400">
                        <SelectValue placeholder="Select language" />
                      </SelectTrigger>
                      <SelectContent className="max-h-[300px]">
                        {LANGUAGES.map((lang) => (
                          <SelectItem key={lang.value} value={lang.value}>
                            {lang.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-gray-700">
                      UserType
                    </Label>
                    <Select value={userType} onValueChange={setUserType}>
                      <SelectTrigger className="border-gray-300 hover:border-gray-400">
                        <SelectValue placeholder="Select usertype" />
                      </SelectTrigger>
                      <SelectContent>
                        {USERTYPES.map((time) => (
                          <SelectItem key={time.value} value={time.value}>
                            {time.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="text-sm font-medium text-gray-700">
                    Upload Document
                  </Label>
                  <Input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.txt,.docx"
                    onChange={handleFileChange}
                    className="border-gray-300 hover:border-gray-400 cursor-pointer"
                  />
                  {fileError && (
                    <div className="text-red-500 text-sm mt-1">{fileError}</div>
                  )}
                </div>

                <div className="space-y-2">
                  <Label className="text-sm font-medium text-gray-700">
                    Legal Area
                  </Label>
                  <RadioGroup
                    value={legalArea}
                    onValueChange={setLegalArea}
                    className="grid grid-cols-2 md:grid-cols-4 gap-4"
                  >
                    {LEGAL_AREAS.map((area) => (
                      <div
                        key={area.value}
                        className="flex items-center space-x-2"
                      >
                        <RadioGroupItem
                          value={area.value}
                          id={area.value}
                          className="border-gray-300 text-gray-900"
                        />
                        <Label
                          htmlFor={area.value}
                          className="text-sm text-gray-700"
                        >
                          {area.label}
                        </Label>
                      </div>
                    ))}
                  </RadioGroup>
                </div>

                {apiError && (
                  <div className="text-red-500 text-sm mt-4 text-center">
                    {apiError}
                  </div>
                )}

                <Button
                  className="w-full bg-gray-900 hover:bg-gray-800 text-white border border-gray-900"
                  onClick={handleStartChat}
                  disabled={!legalArea || !!fileError}
                >
                  Start Chatbot
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : (
        <div className="max-w-7xl mx-auto h-[90vh] flex flex-col p-6">
          <Card className="flex-1 flex flex-col border mb-4">
            <CardContent className="flex-1 flex flex-col p-6 pb-0">
              <div className="flex items-center justify-between mb-6 pb-4 border-b">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">
                    Legal Consultation
                  </h3>
                  <div className="text-sm text-gray-500 mt-1">
                    {language} • {legalArea} •{" "}
                    {USERTYPES.find((t) => t.value === userType)?.label}
                  </div>
                </div>
                <Button
                  variant="outline"
                  onClick={handleReset}
                  className="text-gray-700 hover:bg-gray-50 border-gray-300"
                >
                  Reset Session
                </Button>
              </div>

              <ScrollArea
                ref={scrollAreaRef}
                className="flex-1 pr-4 mb-4"
                onScroll={() => {
                  // Handle manual scroll if needed
                }}
              >
                <div className="space-y-4">
                  {messages.length === 0 && (
                    <div className="text-center text-gray-400 py-12">
                      <div className="text-lg font-medium">
                        Begin your legal consultation
                      </div>
                      <div className="text-sm mt-2">
                        Ask about case law, regulations, or document analysis
                      </div>
                    </div>
                  )}

                  {messages.map((msg, i) => (
                    <div
                      key={i}
                      className={`flex ${
                        msg.role === "user" ? "justify-end" : "justify-start"
                      }`}
                    >
                      
                      <div
                        className={`max-w-[75%] px-4 py-3 rounded-lg ${
                          msg.role === "user"
                            ? "bg-gray-900 text-white"
                            : "bg-gray-50 text-gray-900"
                        }`}
                      >
                        <p>{msg.data_source}</p>
                        {msg.role == "user" ? (
                          msg.content
                        ) : (
                          <div
                            dangerouslySetInnerHTML={{ __html: msg.content }}
                          />
                        )}
                      </div>
                    </div>
                  ))}

                  {loading && (
                    <div className="flex justify-start">
                      <div className="flex items-center gap-3 bg-gray-50 px-4 py-3 rounded-lg">
                        <Loader2 className="animate-spin w-5 h-5 text-gray-500" />
                        <span className="text-gray-600">Analyzing...</span>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </ScrollArea>

              <div className="sticky bottom-0 bg-white pt-4 pb-4">
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSend();
                  }}
                  className="bg-white border-t pt-4"
                >
                  {apiError && (
                    <div className="text-red-500 text-sm mb-2">{apiError}</div>
                  )}
                  <div className="flex gap-3">
                    <Textarea
                      className="flex-1 resize-none min-h-[100px] text-sm border-gray-300"
                      placeholder="Type your legal query..."
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={handleKeyDown}
                      disabled={loading}
                    />
                    <Button
                      type="submit"
                      disabled={loading || !input.trim()}
                      className="self-end bg-gray-900 hover:bg-gray-800 text-white border border-gray-900"
                    >
                      {loading ? (
                        <Loader2 className="animate-spin h-5 w-5" />
                      ) : (
                        "Send"
                      )}
                    </Button>
                  </div>
                  {file && (
                    <div className="text-sm text-gray-500 mt-2 flex items-center gap-2">
                      <span>📎 Attached:</span>
                      <span className="font-medium">{file.name}</span>
                    </div>
                  )}
                </form>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
