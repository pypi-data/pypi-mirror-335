use quick_xml::events::{BytesDecl, BytesEnd, BytesStart, BytesText, Event};
use quick_xml::Writer;

#[derive(Debug, Clone)]
pub enum CellData {
    String(String),
    Number(f64),
    Bool(bool),
}

pub struct SheetWriter {
    pub name: String,
    headers: Vec<String>,
    columns: Vec<Vec<CellData>>,
}

impl SheetWriter {
    pub fn new(name: &str, headers: Vec<String>) -> Self {
        SheetWriter {
            name: name.into(),
            headers,
            columns: Vec::new(),
        }
    }

    pub fn add_column(&mut self, data: Vec<CellData>) {
        self.columns.push(data);
        // println!("add data to sheet: {}", self.name);
    }

    pub fn generate_xml(&self) -> Result<Vec<u8>, std::io::Error> {
        // Preallocate 128 M
        let mut writer = Writer::new(Vec::with_capacity(128 * 1024 * 1024));
        writer.write_event(Event::Decl(BytesDecl::new("1.0", Some("UTF-8"), Some("yes"))))?;

        let mut root = BytesStart::new("worksheet");
        root.push_attribute(("xmlns", "http://schemas.openxmlformats.org/spreadsheetml/2006/main"));
        root.push_attribute(("xmlns:r", "http://schemas.openxmlformats.org/officeDocument/2006/relationships"));
        writer.write_event(Event::Start(root))?;

        writer.write_event(Event::Start(BytesStart::new("sheetData")))?;

        // Precompute column letters
        let column_letters: Vec<String> = (0..self.columns.len()).map(|col_idx| column_index_to_letter(col_idx)).collect();
        // Write headers if present
        let mut header_offset = 2;

        if self.headers.is_empty() {
            header_offset = 1;
        } else {
            let mut row = BytesStart::new("row");
            row.push_attribute(("r", "1"));
            writer.write_event(Event::Start(row))?;

            for (col_idx, header) in self.headers.iter().enumerate() {
                let mut cell = BytesStart::new("c");
                cell.push_attribute(("r", format!("{}1", column_letters[col_idx]).as_str()));

                writer.write_event(Event::Start(cell))?;
                writer.write_event(Event::Start(BytesStart::new("is")))?;
                writer.write_event(Event::Start(BytesStart::new("t")))?;
                writer.write_event(Event::Text(BytesText::new(header)))?;
                writer.write_event(Event::End(BytesEnd::new("t")))?;
                writer.write_event(Event::End(BytesEnd::new("is")))?;
                writer.write_event(Event::End(BytesEnd::new("c")))?;
            }

            writer.write_event(Event::End(BytesEnd::new("row")))?;
        }

        let max_len = self.columns.iter().map(|c| c.len()).max().unwrap_or(0);
        // Write data rows
        for row_idx in 0..max_len {
            let mut row = BytesStart::new("row");
            let excel_row = row_idx + header_offset; // Headers are row 1, data starts at 2
            row.push_attribute(("r", excel_row.to_string().as_str()));
            writer.write_event(Event::Start(row))?;

            for (col_idx, column) in self.columns.iter().enumerate() {
                if let Some(cell_data) = column.get(row_idx) {
                    let mut cell = BytesStart::new("c");
                    cell.push_attribute(("r", format!("{}{}", column_letters[col_idx], excel_row).as_str()));

                    match cell_data {
                        CellData::String(s) => {
                            writer.write_event(Event::Start(cell))?;
                            writer.write_event(Event::Start(BytesStart::new("is")))?;
                            writer.write_event(Event::Start(BytesStart::new("t")))?;
                            writer.write_event(Event::Text(BytesText::new(s)))?;
                            writer.write_event(Event::End(BytesEnd::new("t")))?;
                            writer.write_event(Event::End(BytesEnd::new("is")))?;
                        }
                        CellData::Number(n) => {
                            writer.write_event(Event::Start(cell))?;
                            writer.write_event(Event::Start(BytesStart::new("v")))?;
                            writer.write_event(Event::Text(BytesText::new(&n.to_string())))?;
                            writer.write_event(Event::End(BytesEnd::new("v")))?;
                        }
                        CellData::Bool(b) => {
                            cell.push_attribute(("t", "b"));
                            writer.write_event(Event::Start(cell))?;
                            writer.write_event(Event::Start(BytesStart::new("v")))?;
                            writer.write_event(Event::Text(BytesText::new(if *b { "1" } else { "0" })))?;
                            writer.write_event(Event::End(BytesEnd::new("v")))?;
                        }
                    }
                    writer.write_event(Event::End(BytesEnd::new("c")))?;
                }
            }

            writer.write_event(Event::End(BytesEnd::new("row")))?;
        }

        writer.write_event(Event::End(BytesEnd::new("sheetData")))?;
        writer.write_event(Event::End(BytesEnd::new("worksheet")))?;
        Ok(writer.into_inner())
    }
}

// Helper to convert 0-based column index to Excel column letters (A, B, ..., AA, AB, etc.)
fn column_index_to_letter(n: usize) -> String {
    let mut n = n;
    let mut letters = String::new();
    while n >= 26 {
        letters.insert(0, ((n % 26) as u8 + b'A') as char);
        n = n / 26 - 1;
    }
    letters.insert(0, (n as u8 + b'A') as char);
    letters
}
