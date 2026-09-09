import io, sys
F = sys.argv[1]
src = io.open(F, encoding="utf-8").read()

OLD = """      '<span class="q-eq-badge" data-badge>Add to fleet</span>' +"""
NEW = """      /* 1 Sep — THE CORNER COUNT BADGE IS GONE. Alex: "we also dont need this
         anymore given we have the number selector below."
         Right, and it is the same duplication this pass has cut four times now.
         The badge shrank from "1 in your fleet" to a bare disc precisely because
         it was covering the CafeMatic's hoppers to repeat a control — but the
         Add pill then became a stepper that states the count in words and lets
         you change it, so even a 26px disc is now the number printed twice, one
         of them on the product photo. __paint's writer is guarded with
         if(badge), so it simply no-ops; nothing else reaches for it. */"""
assert src.count(OLD) == 1, "badge anchor not unique: %d" % src.count(OLD)
io.open(F, "w", encoding="utf-8").write(src.replace(OLD, NEW))
print("badge removed")
