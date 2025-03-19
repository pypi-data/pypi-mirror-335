use super::sheet::{CellData, SheetWriter};
use pyo3::prelude::*;
use quick_xml::events::{BytesDecl, BytesEnd, BytesStart, Event};
use quick_xml::Writer;
use std::io::Write;
use zip::write::SimpleFileOptions;
use zip::{CompressionMethod, ZipWriter};

#[pyclass]
pub struct BookWriter {
    sheet_writers: Vec<SheetWriter>,
}

#[pymethods]
impl BookWriter {
    #[new]
    fn new() -> Self {
        BookWriter { sheet_writers: Vec::new() }
    }

    fn add_sheet(&mut self, name: &str, headers: Vec<String>) {
        let sheet_writer = SheetWriter::new(name, headers);
        self.sheet_writers.push(sheet_writer);
    }

    fn add_column_str(&mut self, sheet_idx: usize, series: Vec<String>) {
        let cell_series: Vec<CellData> = series.into_iter().map(CellData::String).collect();
        self.add_column(sheet_idx, cell_series);
    }

    fn add_column_number(&mut self, sheet_idx: usize, series: Vec<f64>) {
        let cell_series: Vec<CellData> = series.into_iter().map(CellData::Number).collect();
        self.add_column(sheet_idx, cell_series);
    }

    fn add_column_bool(&mut self, sheet_idx: usize, series: Vec<bool>) {
        let cell_series: Vec<CellData> = series.into_iter().map(CellData::Bool).collect();
        self.add_column(sheet_idx, cell_series);
    }

    fn save(&mut self, name: &str) {
        if let Err(e) = self.write_xlsx(name) {
            eprintln!("Operation failed: {:?}", e);
        }
    }
}

impl BookWriter {
    fn write_xlsx(&mut self, name: &str) -> Result<(), std::io::Error> {
        let file = std::fs::File::create(name).expect(&format!("create file {name} error!"));
        let mut zip_writer = ZipWriter::new(file);
        let options = SimpleFileOptions::default().compression_method(CompressionMethod::Deflated);

        // [Content_Types].xml
        let content_types = self.write_content_types().expect("fail to write: [Content_Types].xml");
        zip_writer.start_file("[Content_Types].xml", options)?;
        zip_writer.write_all(&content_types)?;

        // _rels/.rels
        let root_rels = self.write_root_rels().expect("fail to write: _rels/.rels");
        zip_writer.start_file("_rels/.rels", options)?;
        zip_writer.write_all(&root_rels)?;

        // xl/workbook.xml
        let workbook_xml = self.write_workbook().expect("failed to write: xl/workbook.xml");
        zip_writer.start_file("xl/workbook.xml", options)?;
        zip_writer.write_all(&workbook_xml)?;

        // xl/styles.xml
        let styles = self.write_styles().expect("failed to write: xl/styles.xml");
        zip_writer.start_file("xl/styles.xml", options)?;
        zip_writer.write_all(&styles)?;

        // xl/_rels/workbook.xml.rels
        let workbook_rels = self.write_workbook_rels().expect("failed to write: xl/_rels/workbook.xml.rels");
        zip_writer.start_file("xl/_rels/workbook.xml.rels", options)?;
        zip_writer.write_all(&workbook_rels)?;

        // xl/worksheets/sheet*.xml
        for (sheet_idx, sheet_writer) in self.sheet_writers.iter().enumerate() {
            zip_writer.start_file(&format!("xl/worksheets/sheet{}.xml", sheet_idx + 1), options)?;
            zip_writer.write_all(&sheet_writer.generate_xml()?)?;
        }
        zip_writer.finish()?;
        Ok(())
    }

    fn add_column(&mut self, sheet_idx: usize, series: Vec<CellData>) {
        if let Some(sheet_writer) = self.sheet_writers.get_mut(sheet_idx) {
            sheet_writer.add_column(series);
        } else {
            println!("add column failed, sheet_idx should in [0, {}]", self.sheet_writers.len());
        }
    }

    fn write_styles(&mut self) -> Result<Vec<u8>, std::io::Error> {
        let mut writer = Writer::new(Vec::new());
        writer.write_event(Event::Decl(BytesDecl::new("1.0", Some("UTF-8"), Some("yes"))))?;

        let mut root = BytesStart::new("styleSheet");
        root.push_attribute(("xmlns", "http://schemas.openxmlformats.org/spreadsheetml/2006/main"));
        writer.write_event(Event::Start(root))?;
        writer.write_event(Event::End(BytesEnd::new("styleSheet")))?;
        Ok(writer.into_inner())
    }

    fn write_root_rels(&mut self) -> Result<Vec<u8>, std::io::Error> {
        let mut writer = Writer::new(Vec::new());
        writer.write_event(Event::Decl(BytesDecl::new("1.0", Some("UTF-8"), Some("yes"))))?;

        let mut root = BytesStart::new("Relationships");
        root.push_attribute(("xmlns", "http://schemas.openxmlformats.org/package/2006/relationships"));
        writer.write_event(Event::Start(root))?;
        writer.write_event(Event::Empty(BytesStart::new("Relationship").with_attributes(vec![
            ("Id", "rId1"),
            (
                "Type",
                "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument",
            ),
            ("Target", "xl/workbook.xml"),
        ])))?;

        writer.write_event(Event::End(BytesEnd::new("Relationships")))?;
        Ok(writer.into_inner())
    }

    fn write_content_types(&mut self) -> Result<Vec<u8>, std::io::Error> {
        let mut writer = Writer::new(Vec::new());
        writer.write_event(Event::Decl(BytesDecl::new("1.0", Some("UTF-8"), Some("yes"))))?;

        let mut root = BytesStart::new("Types");
        root.push_attribute(("xmlns", "http://schemas.openxmlformats.org/package/2006/content-types"));
        writer.write_event(Event::Start(root))?;

        // Defaults
        writer.write_event(Event::Empty(BytesStart::new("Default").with_attributes(vec![
            ("Extension", "rels"),
            ("ContentType", "application/vnd.openxmlformats-package.relationships+xml"),
        ])))?;

        // Workbook
        writer.write_event(Event::Empty(BytesStart::new("Override").with_attributes(vec![
            ("PartName", "/xl/workbook.xml"),
            (
                "ContentType",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml",
            ),
        ])))?;

        // Worksheets (use index-based filenames)
        for (idx, _) in self.sheet_writers.iter().enumerate() {
            writer.write_event(Event::Empty(BytesStart::new("Override").with_attributes(vec![
                ("PartName", format!("/xl/worksheets/sheet{}.xml", idx + 1).as_str()),
                ("ContentType", "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"),
            ])))?;
        }

        writer.write_event(Event::End(BytesEnd::new("Types")))?;
        Ok(writer.into_inner())
    }

    fn write_workbook_rels(&mut self) -> Result<Vec<u8>, std::io::Error> {
        let mut writer = Writer::new(Vec::new());
        writer.write_event(Event::Decl(BytesDecl::new("1.0", Some("UTF-8"), Some("yes"))))?;

        let mut root = BytesStart::new("Relationships");
        root.push_attribute(("xmlns", "http://schemas.openxmlformats.org/package/2006/relationships"));
        writer.write_event(Event::Start(root))?;

        // Worksheet relationships (use index-based filenames)
        for (idx, _) in self.sheet_writers.iter().enumerate() {
            writer.write_event(Event::Empty(BytesStart::new("Relationship").with_attributes(vec![
                ("Id", format!("rId{}", idx + 1).as_str()),
                ("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"),
                ("Target", &format!("worksheets/sheet{}.xml", idx + 1)),
            ])))?;
        }

        writer.write_event(Event::End(BytesEnd::new("Relationships")))?;
        Ok(writer.into_inner())
    }

    fn write_workbook(&mut self) -> Result<Vec<u8>, std::io::Error> {
        let mut writer = Writer::new(Vec::new());
        writer.write_event(Event::Decl(BytesDecl::new("1.0", Some("UTF-8"), Some("yes"))))?;

        let mut root = BytesStart::new("workbook");
        root.push_attribute(("xmlns", "http://schemas.openxmlformats.org/spreadsheetml/2006/main"));
        root.push_attribute(("xmlns:r", "http://schemas.openxmlformats.org/officeDocument/2006/relationships"));
        writer.write_event(Event::Start(root))?;

        writer.write_event(Event::Start(BytesStart::new("sheets")))?;

        // Generate sheets in insertion order with correct rIds
        for (idx, sheet_writer) in self.sheet_writers.iter().enumerate() {
            let mut sheet = BytesStart::new("sheet");
            sheet.push_attribute(("name", sheet_writer.name.as_str()));
            sheet.push_attribute(("sheetId", (idx + 1).to_string().as_str()));
            sheet.push_attribute(("r:id", format!("rId{}", idx + 1).as_str()));
            writer.write_event(Event::Empty(sheet))?;
        }

        writer.write_event(Event::End(BytesEnd::new("sheets")))?;
        writer.write_event(Event::End(BytesEnd::new("workbook")))?;
        Ok(writer.into_inner())
    }
}
