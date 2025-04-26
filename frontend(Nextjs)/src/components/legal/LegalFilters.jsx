
import { Label } from "@/components/ui/label";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";

function LegalFilters({
  language,
  setLanguage,
  legalArea,
  setLegalArea,
  timeframe,
  setTimeframe,
}) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="space-y-2">
          <Label htmlFor="language" className="text-sm font-medium">Language</Label>
          <Select value={language} onValueChange={setLanguage}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select language" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="English">English</SelectItem>
              <SelectItem value="Hindi">हिन्दी</SelectItem>
              <SelectItem value="Bengali">বাংলা</SelectItem>
              <SelectItem value="Telugu">తెలుగు</SelectItem>
              <SelectItem value="Tamil">தமிழ்</SelectItem>
              <SelectItem value="Marathi">मराठी</SelectItem>
              <SelectItem value="Gujarati">ગુજરાતી</SelectItem>
              <SelectItem value="Kannada">ಕನ್ನಡ</SelectItem>
              <SelectItem value="Malayalam">മലയാളം</SelectItem>
              <SelectItem value="Punjabi">ਪੰਜਾਬੀ</SelectItem>
              <SelectItem value="Odia">ଓଡ଼ିଆ</SelectItem>
              <SelectItem value="Assamese">অসমীয়া</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label className="text-sm font-medium">Legal Area</Label>
          <RadioGroup
            value={legalArea}
            onValueChange={setLegalArea}
            className="flex flex-wrap gap-4"
          >
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="IPC" id="ipc" />
              <Label htmlFor="ipc">IPC</Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="RTI" id="rti" />
              <Label htmlFor="rti">RTI</Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="Labor" id="labor" />
              <Label htmlFor="labor">Labor Laws</Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="Other" id="other" />
              <Label htmlFor="other">Other</Label>
            </div>
          </RadioGroup>
        </div>

        <div className="space-y-2">
          <Label htmlFor="timeframe" className="text-sm font-medium">Timeframe</Label>
          <Select value={timeframe} onValueChange={setTimeframe}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select timeframe" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all-time">All Time</SelectItem>
              <SelectItem value="past-year">Past Year</SelectItem>
              <SelectItem value="past-month">Past Month</SelectItem>
              <SelectItem value="past-week">Past Week</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
}

export {LegalFilters};