const express = require("express");
const cors = require("cors");
const multer = require("multer");
const path = require("path");
const fs = require("fs");

const app = express();
app.use(cors());
app.use(express.json());
app.use("/images", express.static(path.join(__dirname, "public/images")));

let projects = []; // Simpan sementara (nanti bisa dipindah ke DB)

// Multer config
const storage = multer.diskStorage({
  destination: "public/images/",
  filename: (req, file, cb) => {
    cb(null, Date.now() + "-" + file.originalname);
  },
});
const upload = multer({ storage });

// ========== GET ALL PROJECTS ==========
app.get("/projects", (req, res) => {
  res.json(projects);
});

// ========== CREATE PROJECT ==========
app.post("/projects", upload.single("image"), (req, res) => {
  const { name, link } = req.body;

  const newProject = {
    id: Date.now(),
    name,
    link,
    image: req.file
      ? `http://localhost:5000/images/${req.file.filename}`
      : null,
  };

  projects.push(newProject);
  res.json({ message: "Project added", project: newProject });
});

// ========== UPDATE PROJECT ==========
app.put("/projects/:id", upload.single("image"), (req, res) => {
  const projectId = parseInt(req.params.id);
  const { name, link } = req.body;

  const index = projects.findIndex((p) => p.id === projectId);
  if (index === -1) return res.status(404).json({ message: "Not found" });

  // If user uploaded new image → delete old
  if (req.file) {
    const oldImage = projects[index].image?.replace(
      "http://localhost:5000/images/",
      ""
    );
    fs.unlink(`public/images/${oldImage}`, () => {});
  }

  projects[index] = {
    ...projects[index],
    name,
    link,
    image: req.file
      ? `http://localhost:5000/images/${req.file.filename}`
      : projects[index].image,
  };

  res.json({ message: "Project updated", project: projects[index] });
});

// ========== DELETE PROJECT ==========
app.delete("/projects/:id", (req, res) => {
  const projectId = parseInt(req.params.id);
  const index = projects.findIndex((p) => p.id === projectId);

  if (index === -1) return res.status(404).json({ message: "Not found" });

  // Delete image file
  const oldImage = projects[index].image?.replace(
    "http://localhost:5000/images/",
    ""
  );
  fs.unlink(`public/images/${oldImage}`, () => {});

  const removed = projects.splice(index, 1);
  res.json({ message: "Project deleted", removed });
});

app.listen(5000, () => {
  console.log("Backend running on http://localhost:5000");
});
