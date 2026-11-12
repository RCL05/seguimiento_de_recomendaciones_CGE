// Pre-render de Quarto: copia las fuentes editables de diagramas desde
// DOCUMENTACION/**/DIAGRAMAS/ a docs/assets/diagrams/src/ para publicarlas en el sitio.
// La única fuente de verdad sigue siendo DOCUMENTACION/; la carpeta destino está en .gitignore.
const projectDir = Deno.env.get("QUARTO_PROJECT_DIR") ?? Deno.cwd();
const sep = projectDir.includes("\\") ? "\\" : "/";
const join = (...parts: string[]) => parts.join(sep);

const sources = [
  join(projectDir, "..", "DOCUMENTACION", "02_PROCESOS", "DIAGRAMAS"),
  join(projectDir, "..", "DOCUMENTACION", "03_ARQUITECTURA", "DIAGRAMAS"),
];
const target = join(projectDir, "assets", "diagrams", "src");
await Deno.mkdir(target, { recursive: true });

let copied = 0;
for (const dir of sources) {
  try {
    for await (const entry of Deno.readDir(dir)) {
      if (entry.isFile && /\.(bpmn|dsl|puml)$/i.test(entry.name)) {
        await Deno.copyFile(join(dir, entry.name), join(target, entry.name));
        copied++;
      }
    }
  } catch (error) {
    console.error(`sync-diagrams: no se pudo leer ${dir}: ${error}`);
  }
}
console.log(`sync-diagrams: ${copied} fuentes copiadas a ${target}`);
