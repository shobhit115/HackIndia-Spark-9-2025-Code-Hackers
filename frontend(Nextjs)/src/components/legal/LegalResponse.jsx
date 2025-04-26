import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function LegalResponse({ answer, citations }) {
  return (
    <Card className="mt-6 bg-white border border-black">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-black">Legal Answer</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm leading-relaxed text-gray-700">{answer}</p>
        {citations && (
          <div className="border-t border-black pt-4">
            <p className="text-xs text-gray-600">
              <span className="font-medium text-black">Citations:</span> {citations}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
