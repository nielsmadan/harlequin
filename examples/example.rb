class Convertor < Formula
  desc "Convert between units of measurement"
  homepage "https://github.com/example/convertor"
  url "https://github.com/example/convertor/archive/v2.1.0.tar.gz"
  sha256 "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
  license "MIT"
  head "https://github.com/example/convertor.git", branch: "main"

  bottle do
    sha256 cellar: :any_skip_relocation, arm64_sonoma: "abc123"
    sha256 cellar: :any_skip_relocation, sonoma:       "def456"
    sha256 cellar: :any_skip_relocation, x86_64_linux: "789abc"
  end

  depends_on "rust" => :build
  depends_on "openssl@3"

  def install
    system "cargo", "build", "--release"
    bin.install "target/release/convertor"

    generate_completions_from_executable(
      bin/"convertor", "completions",
      base_name: "convertor",
      shells: [:bash, :zsh, :fish]
    )

    man1.install "docs/convertor.1"
  end

  test do
    output = shell_output("#{bin}/convertor 100 km miles")
    assert_match "62.137", output

    # Test temperature conversion
    result = shell_output("#{bin}/convertor 0 celsius fahrenheit")
    assert_equal "32", result.strip

    # Test error handling
    assert_match "Unknown unit",
      shell_output("#{bin}/convertor 1 foo bar 2>&1", 1)

    # Verify version string
    version_output = shell_output("#{bin}/convertor --version")
    assert_match version.to_s, version_output
  end

  private

  def post_install
    config_dir = etc/"convertor"
    config_dir.mkpath

    unless (config_dir/"units.yaml").exist?
      (config_dir/"units.yaml").write <<~YAML
        custom_units:
          - name: "smoots"
            base: "meters"
            factor: 1.7018
      YAML
    end
  end
end
