export interface AIDebugTrace {
  query: string;
  filters: any;
  retrieved_items: VisionMatch[];
  matches?: VisionMatch[];
  vision_description?: string;
  raw: any;
}

export interface VisionMatch {
  id: string | null;
  title: string;
  origin?: string;
  category?: string;
  price?: number;
  tags: string[];
  flavor_profiles: string[];
  dietary_features: string[];
  distance?: number;
}